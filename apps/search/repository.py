# =============================================================================
# FILE: apps/search/repository.py
#
# Implements two query strategies, both using EXISTING indexes:
#   1. autocomplete_search()  — ultra-fast typeahead (statement_timeout 3s)
#   2. unified_search()       — ranked cross-entity search  (timeout 8s)
#
# PRODUCTION SAFETY MEASURES:
#   - Every raw SQL block runs inside SET LOCAL statement_timeout so a slow
#     query can never hold a DB connection open indefinitely.
#   - pg_trgm absence is caught as SearchUnavailableError; callers degrade
#     gracefully to icontains-only results.
#   - All user input is passed as parameterised %s — never interpolated.
#   - Minimum query length of 2 chars enforced at view layer (not here) to
#     avoid full-table scans on single-character inputs.
#   - OCR text search uses the GIN tsvector index from migration 0003.
#   - FileAttachment.file_name uses trigram index (migration 0002 covers
#     OCR text; file_name gets icontains fallback — acceptable for filenames).
# =============================================================================
import logging
from django.db import connection, OperationalError, ProgrammingError
from apps.search.exceptions import SearchUnavailableError

logger = logging.getLogger(__name__)

# Hard limits — never let a caller exceed these
_AUTOCOMPLETE_HARD_LIMIT = 50
_UNIFIED_HARD_LIMIT      = 200

# Timeouts (PostgreSQL SET LOCAL statement_timeout syntax)
_AUTOCOMPLETE_TIMEOUT = "3s"
_UNIFIED_TIMEOUT      = "8s"


def _run_with_timeout(cursor, timeout: str, sql: str, params: list):
    """Execute sql with a LOCAL statement_timeout. Raises SearchUnavailableError
    on timeout or missing pg_trgm extension instead of letting exceptions
    propagate as HTTP 500."""
    try:
        cursor.execute(f"SET LOCAL statement_timeout = '{timeout}'")
        cursor.execute(sql, params)
    except OperationalError as exc:
        # statement_timeout fires as OperationalError with 'canceling statement'
        raise SearchUnavailableError(
            f'Search query timed out after {timeout}. Try a more specific term.'
        ) from exc
    except ProgrammingError as exc:
        msg = str(exc).lower()
        if 'similarity' in msg or 'pg_trgm' in msg:
            raise SearchUnavailableError(
                'pg_trgm extension not installed. Run: '
                'CREATE EXTENSION IF NOT EXISTS pg_trgm;'
            ) from exc
        raise


def autocomplete_search(q: str, limit: int = 10) -> list[dict]:
    """
    Returns up to `limit` lightweight suggestions across:
      - Document.document_number  (exact prefix match prioritised)
      - Document.title            (trigram)
      - FileAttachment.file_name  (icontains)

    Each result contains only the minimum fields needed for a dropdown:
      id, document_number, title, file_name, file_type, match_source

    Designed to complete in < 100 ms on a LAN PostgreSQL instance with
    the existing trigram index on edms_document.
    """
    limit = min(int(limit), _AUTOCOMPLETE_HARD_LIMIT)
    sql = """
        SELECT
            d.id,
            d.document_number,
            d.title,
            d.status,
            NULL::text   AS file_name,
            NULL::text   AS file_type,
            'document'   AS match_source,
            CASE
                WHEN lower(d.document_number) LIKE lower(%s) THEN 1.0
                ELSE COALESCE(
                    similarity(d.document_number || ' ' || d.title, %s), 0
                )
            END AS rank
        FROM edms_document d
        WHERE
            d.document_number ILIKE %s
            OR d.title        ILIKE %s
            OR d.keywords     ILIKE %s

        UNION ALL

        SELECT
            d.id,
            d.document_number,
            d.title,
            d.status,
            fa.file_name,
            fa.file_type,
            'filename'   AS match_source,
            0.5          AS rank
        FROM edms_file_attachment fa
        JOIN edms_revision        rev ON rev.id          = fa.revision_id
        JOIN edms_document        d   ON d.id            = rev.document_id
        WHERE fa.file_name ILIKE %s

        ORDER BY rank DESC, document_number
        LIMIT %s;
    """
    like_q   = f'%{q}%'
    prefix_q = f'{q}%'
    params   = [prefix_q, q, like_q, like_q, like_q, like_q, limit]

    with connection.cursor() as cursor:
        _run_with_timeout(cursor, _AUTOCOMPLETE_TIMEOUT, sql, params)
        cols = [col[0] for col in cursor.description]
        rows = cursor.fetchall()

    return [dict(zip(cols, row)) for row in rows]


def unified_search(q: str, limit: int = 25, offset: int = 0) -> dict:
    """
    Cross-entity ranked search across ALL searchable surfaces:
      1. Document metadata   (document_number, title, keywords, eoffice fields)
      2. FileAttachment name (file_name)
      3. OCR full text       (uses GIN tsvector index from migration 0003)
      4. Document notes      (note_text icontains)
      5. Correspondents      (name, short_code)

    Results are UNION-ed, de-duplicated by document id, then ranked by
    match_source priority:
        doc_number=5  >  title=4  >  keyword=3  >  filename=2  >  ocr=1.5  >
        note=1  >  correspondent=0.8

    Returns:
        {
          'count':   <total rows before pagination>,
          'results': [ {id, document_number, title, status, file_name,
                        file_type, match_source, snippet, rank}, ... ]
        }
    """
    limit  = min(int(limit),  _UNIFIED_HARD_LIMIT)
    offset = max(int(offset), 0)

    # Build tsquery safely — wrap in plainto_tsquery to avoid syntax errors
    # from user input containing special tsquery characters.
    sql = """
        WITH ranked AS (

            -- Source 1: document metadata (doc_number, title, keywords, eoffice)
            SELECT
                d.id,
                d.document_number,
                d.title,
                d.status,
                NULL::text          AS file_name,
                NULL::text          AS file_type,
                'doc_number'        AS match_source,
                NULL::text          AS snippet,
                CASE
                    WHEN d.document_number ILIKE %s THEN 5.0
                    WHEN d.title           ILIKE %s THEN 4.0
                    WHEN d.keywords        ILIKE %s THEN 3.0
                    ELSE 2.5
                END                 AS rank
            FROM edms_document d
            WHERE
                d.document_number       ILIKE %s
                OR d.title              ILIKE %s
                OR d.keywords           ILIKE %s
                OR d.eoffice_file_number ILIKE %s
                OR d.eoffice_subject    ILIKE %s
                OR d.description        ILIKE %s

            UNION ALL

            -- Source 2: FileAttachment file_name
            SELECT
                d.id,
                d.document_number,
                d.title,
                d.status,
                fa.file_name,
                fa.file_type,
                'filename'          AS match_source,
                fa.file_name        AS snippet,
                2.0                 AS rank
            FROM edms_file_attachment fa
            JOIN edms_revision        rev ON rev.id = fa.revision_id
            JOIN edms_document        d   ON d.id   = rev.document_id
            WHERE fa.file_name ILIKE %s

            UNION ALL

            -- Source 3: OCR full text via GIN tsvector index
            SELECT
                d.id,
                d.document_number,
                d.title,
                d.status,
                fa.file_name,
                fa.file_type,
                'ocr_text'          AS match_source,
                left(ocr.full_text, 200) AS snippet,
                1.5                 AS rank
            FROM ocr_ocrresult     ocr
            JOIN ocr_ocrqueue      q   ON q.id  = ocr.queue_id
            JOIN edms_file_attachment fa ON fa.id = q.file_attachment_id
            JOIN edms_revision        rev ON rev.id = fa.revision_id
            JOIN edms_document        d   ON d.id   = rev.document_id
            WHERE to_tsvector('english', COALESCE(ocr.full_text, ''))
                  @@ plainto_tsquery('english', %s)

            UNION ALL

            -- Source 4: Document notes
            SELECT
                d.id,
                d.document_number,
                d.title,
                d.status,
                NULL::text          AS file_name,
                NULL::text          AS file_type,
                'note'              AS match_source,
                left(dn.note_text, 200) AS snippet,
                1.0                 AS rank
            FROM edms_document_note dn
            JOIN edms_document      d  ON d.id = dn.document_id
            WHERE dn.note_text ILIKE %s

            UNION ALL

            -- Source 5: Correspondent name / short_code
            SELECT
                d.id,
                d.document_number,
                d.title,
                d.status,
                NULL::text          AS file_name,
                NULL::text          AS file_type,
                'correspondent'     AS match_source,
                c.name || ' (' || c.short_code || ')' AS snippet,
                0.8                 AS rank
            FROM edms_correspondent          c
            JOIN edms_document_correspondent_link dcl ON dcl.correspondent_id = c.id
            JOIN edms_document                    d   ON d.id = dcl.document_id
            WHERE c.name ILIKE %s OR c.short_code ILIKE %s
        ),

        -- De-duplicate: keep highest-ranked match_source per document
        deduped AS (
            SELECT DISTINCT ON (id)
                id, document_number, title, status,
                file_name, file_type, match_source, snippet, rank
            FROM ranked
            ORDER BY id, rank DESC
        )

        SELECT
            COUNT(*) OVER ()   AS total_count,
            id, document_number, title, status,
            file_name, file_type, match_source, snippet, rank
        FROM deduped
        ORDER BY rank DESC, document_number
        LIMIT %s OFFSET %s;
    """
    like_q = f'%{q}%'
    params = [
        # Source 1 CASE branches
        like_q, like_q, like_q,
        # Source 1 WHERE
        like_q, like_q, like_q, like_q, like_q, like_q,
        # Source 2 (filename)
        like_q,
        # Source 3 (OCR tsvector)
        q,
        # Source 4 (notes)
        like_q,
        # Source 5 (correspondent x2)
        like_q, like_q,
        # LIMIT / OFFSET
        limit, offset,
    ]

    with connection.cursor() as cursor:
        _run_with_timeout(cursor, _UNIFIED_TIMEOUT, sql, params)
        cols  = [col[0] for col in cursor.description]
        rows  = cursor.fetchall()

    if not rows:
        return {'count': 0, 'results': []}

    total   = rows[0][0]   # total_count window function
    results = []
    for row in rows:
        row_dict = dict(zip(cols, row))
        row_dict.pop('total_count', None)
        results.append(row_dict)

    return {'count': total, 'results': results}

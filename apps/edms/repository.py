# =============================================================================
# FILE: apps/edms/repository.py
# FIXES applied (scenarios from crash/overload audit):
#   #1  - pg_trgm extension guard in get_similar_documents()
#   #5  - fulltext_search no longer joins OCR table (removed 4-level join)
#   #11 - fulltext_search sanitises LIKE-injection chars (%,_,\) from query
#   #18 - get_similar_documents() sets LOCAL statement_timeout = 5s
# =============================================================================
import re
from django.db import connection, ProgrammingError
from django.db.models import Q, Count, Prefetch
from apps.edms.models import Document, Revision, FileAttachment

# Characters that would cause LIKE operator backtracking (ReDoS via DB)
_LIKE_ESCAPE_RE = re.compile(r'[%_\\]')


def _sanitise_search(q: str) -> str:
    """FIX #11: Strip LIKE special chars to prevent ReDoS/slow queries."""
    return _LIKE_ESCAPE_RE.sub('', q).strip()


class DocumentRepository:
    @staticmethod
    def get_list_qs():
        return (
            Document.objects
            .select_related('category', 'section', 'document_type', 'created_by')
            .prefetch_related(
                Prefetch(
                    'revisions',
                    queryset=Revision.objects.only(
                        'id', 'document_id', 'revision_number', 'revision_date'
                    ).order_by('-revision_date', '-created_at'),
                )
            )
            .annotate(revision_count=Count('revisions', distinct=True))
        )

    @staticmethod
    def get_detail_qs():
        return (
            Document.objects
            .select_related('category', 'section', 'document_type', 'created_by')
            .prefetch_related(
                Prefetch(
                    'revisions',
                    queryset=(
                        Revision.objects
                        .select_related('created_by')
                        .prefetch_related(
                            Prefetch(
                                'files',
                                queryset=FileAttachment.objects.only(
                                    'id', 'revision_id', 'file_name', 'file_path',
                                    'file_size_bytes', 'file_type', 'page_count',
                                ),
                            )
                        )
                        .order_by('-revision_date', '-created_at')
                    ),
                )
            )
        )

    @staticmethod
    def fulltext_search(q: str):
        """
        FIX #5:  Removed revisions__files__ocr_result__full_text join — that
                 4-level cross join caused 60s+ queries on large datasets.
                 OCR full-text search should go through a dedicated /ocr/search/
                 endpoint with a proper GIN/tsvector index.
        FIX #11: Query string is sanitised against LIKE special chars before use.
        """
        safe_q = _sanitise_search(q)
        if not safe_q:
            return Document.objects.none()
        return (
            Document.objects
            .filter(
                Q(document_number__icontains=safe_q)
                | Q(title__icontains=safe_q)
                | Q(keywords__icontains=safe_q)
                | Q(eoffice_file_number__icontains=safe_q)
                | Q(eoffice_subject__icontains=safe_q)
            )
            .select_related('category', 'section')
            .annotate(revision_count=Count('revisions', distinct=True))
            .distinct()
        )

    @staticmethod
    def documents_by_section():
        return (
            Document.objects
            .values('section__name')
            .annotate(count=Count('id'))
            .order_by('-count')
        )

    # -------------------------------------------------------------------------
    # SPRINT 2 — Feature #8: Similarity Search
    # -------------------------------------------------------------------------
    SIMILARITY_THRESHOLD = 0.08
    SIMILARITY_LIMIT     = 10

    @classmethod
    def get_similar_documents(
        cls,
        document_id: int,
        limit: int = None,
        threshold: float = None,
    ) -> list[dict]:
        """
        FIX #1:  Wraps the query in a pg_trgm availability check.
                 Returns [] with a warning log if extension is missing
                 instead of crashing with ProgrammingError.
        FIX #18: Sets LOCAL statement_timeout = 5s to prevent runaway
                 trigram scans from hanging DB connections indefinitely.
        """
        import logging
        logger = logging.getLogger(__name__)

        limit     = limit     or cls.SIMILARITY_LIMIT
        threshold = threshold or cls.SIMILARITY_THRESHOLD

        sql = """
            SELECT
                d.id,
                d.document_number,
                d.title,
                d.status,
                c.name   AS category_name,
                dt.name  AS document_type_name,
                ROUND(
                    CAST(
                        similarity(
                            d.title || ' ' || COALESCE(d.keywords, ''),
                            src.combined
                        ) AS NUMERIC
                    ), 4
                ) AS similarity_score
            FROM edms_document d
            LEFT JOIN edms_category      c  ON c.id  = d.category_id
            LEFT JOIN edms_document_type dt ON dt.id = d.document_type_id
            CROSS JOIN (
                SELECT title || ' ' || COALESCE(keywords, '') AS combined
                FROM   edms_document
                WHERE  id = %s
            ) src
            WHERE
                d.id != %s
                AND similarity(
                        d.title || ' ' || COALESCE(d.keywords, ''),
                        src.combined
                    ) > %s
            ORDER BY similarity_score DESC
            LIMIT %s;
        """
        try:
            with connection.cursor() as cursor:
                # FIX #18: 5-second hard cap on this query
                cursor.execute("SET LOCAL statement_timeout = '5s'")
                cursor.execute(sql, [document_id, document_id, threshold, limit])
                columns = [col[0] for col in cursor.description]
                rows    = cursor.fetchall()
        except ProgrammingError as exc:
            # FIX #1: pg_trgm not installed — degrade gracefully
            if 'similarity' in str(exc).lower() or 'pg_trgm' in str(exc).lower():
                logger.warning(
                    'pg_trgm extension is not installed. '
                    'Run: CREATE EXTENSION IF NOT EXISTS pg_trgm; '
                    'Similarity search disabled until then.'
                )
                return []
            raise
        except Exception as exc:
            # Timeout or other DB error — degrade gracefully
            logger.warning('get_similar_documents failed (doc=%s): %s', document_id, exc)
            return []

        return [dict(zip(columns, row)) for row in rows]


class RevisionRepository:
    @staticmethod
    def get_list_qs():
        return (
            Revision.objects
            .select_related('document', 'created_by')
            .prefetch_related(
                Prefetch(
                    'files',
                    queryset=FileAttachment.objects.only(
                        'id', 'revision_id', 'file_name', 'ocr_status'
                    ),
                )
            )
        )

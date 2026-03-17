# =============================================================================
# FILE: apps/edms/repository.py
# SPRINT 2 addition:
#   - DocumentRepository.get_similar_documents()  (Feature #8)
# All existing methods preserved exactly.
# =============================================================================
from django.db import connection
from django.db.models import Q, Count, Prefetch
from apps.edms.models import Document, Revision, FileAttachment


class DocumentRepository:
    @staticmethod
    def get_list_qs():
        return (
            Document.objects
            .select_related('category', 'section', 'document_type', 'created_by')
            .prefetch_related(
                Prefetch('revisions', queryset=Revision.objects.only('id', 'document_id'))
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
        return (
            Document.objects
            .filter(
                Q(document_number__icontains=q)
                | Q(title__icontains=q)
                | Q(keywords__icontains=q)
                | Q(eoffice_file_number__icontains=q)
                | Q(eoffice_subject__icontains=q)
                | Q(revisions__files__ocr_result__full_text__icontains=q)
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
    # Uses pg_trgm similarity() function via raw SQL.
    # Threshold 0.08 is deliberately low for RDSO-style alphanumeric titles
    # (e.g. "RDSO/2016/EL/SPEC/0071") which have modest word overlap.
    # Adjust SIMILARITY_THRESHOLD in settings.py to tune.
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
        Returns up to `limit` documents most similar to `document_id`
        using PostgreSQL trigram similarity on (title || ' ' || keywords).

        Returns a list of dicts:
          [{
              'id': int,
              'document_number': str,
              'title': str,
              'status': str,
              'category_name': str,
              'document_type_name': str,
              'similarity_score': float,   # 0.0 – 1.0
          }, ...]
        """
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
            LEFT JOIN edms_category     c  ON c.id  = d.category_id
            LEFT JOIN edms_document_type dt ON dt.id = d.document_type_id

            -- Get the source document's combined text in one sub-select
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

        with connection.cursor() as cursor:
            cursor.execute(sql, [document_id, document_id, threshold, limit])
            columns = [col[0] for col in cursor.description]
            rows    = cursor.fetchall()

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

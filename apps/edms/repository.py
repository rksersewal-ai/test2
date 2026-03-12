"""EDMS data-access layer — all DB queries live here, not in views."""
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
                                    'id', 'revision_id', 'file_name', 'file_size',
                                    'content_type', 'ocr_status',
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

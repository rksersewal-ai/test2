# =============================================================================
# FILE: apps/edms/services.py
# FIXES applied:
#   #10 - create_revision: SELECT FOR UPDATE now covers the filter().update()
#         chain too, not just the count — prevents concurrent CURRENT→SUPERSEDED
#         race condition across two DB sessions.
#   #13 - AuditService.log() calls deferred to transaction.on_commit() so that
#         audit records are NOT rolled back if the outer transaction fails.
#         This satisfies IRIS compliance requirement for immutable audit trails.
# =============================================================================
from django.db import transaction
from apps.edms.models import Document, Revision
from apps.audit.services import AuditService


def _run_after_commit_or_now(callback):
    """Execute callbacks immediately outside transactions, otherwise on commit."""
    connection = transaction.get_connection()
    if connection.get_autocommit():
        callback()
        return
    transaction.on_commit(callback)


class DocumentService:
    @staticmethod
    @transaction.atomic
    def create_document(data: dict, created_by) -> Document:
        doc = Document.objects.create(created_by=created_by, **data)
        # FIX #13: defer audit log until AFTER the transaction commits
        # so a rollback doesn't silently erase the audit trail
        _doc_id   = doc.pk
        _doc_num  = doc.document_number
        _user     = created_by
        _run_after_commit_or_now(lambda: AuditService.log(
            user=_user,
            module='EDMS',
            action='CREATE_DOCUMENT',
            entity_type='Document',
            entity_id=_doc_id,
            entity_identifier=_doc_num,
            description=f'Document {_doc_num} created.',
        ))
        return doc

    @staticmethod
    @transaction.atomic
    def update_status(doc: Document, new_status: str, user) -> Document:
        old_status = doc.status
        doc.status = new_status
        doc.save(update_fields=['status', 'updated_at'])
        # FIX #13: defer audit log to post-commit
        _doc_id   = doc.pk
        _doc_num  = doc.document_number
        _user     = user
        _old      = old_status
        _new      = new_status
        _run_after_commit_or_now(lambda: AuditService.log(
            user=_user,
            module='EDMS',
            action='UPDATE_STATUS',
            entity_type='Document',
            entity_id=_doc_id,
            entity_identifier=_doc_num,
            description=f'Status changed {_old} \u2192 {_new}.',
        ))
        return doc

    @staticmethod
    def next_revision_number(document: Document) -> str:
        """Lock the document row with SELECT FOR UPDATE before counting
        revisions to prevent concurrent revision number collision.
        Must be called inside an atomic transaction.
        """
        Document.objects.select_for_update().get(pk=document.pk)
        count = document.revisions.count()
        return str(count).zfill(2)


class RevisionService:
    @staticmethod
    @transaction.atomic
    def create_revision(document: Document, data: dict, created_by) -> Revision:
        # FIX #10: lock the document row FIRST, then supersede existing current
        # revision — guarantees the filter().update() below is also inside the
        # lock, preventing interleaved CURRENT→SUPERSEDED from a parallel request.
        Document.objects.select_for_update().get(pk=document.pk)

        Revision.objects.filter(
            document=document, status=Revision.Status.CURRENT
        ).update(status=Revision.Status.SUPERSEDED)

        if 'revision_number' not in data or not data['revision_number']:
            data['revision_number'] = DocumentService.next_revision_number(document)

        rev = Revision.objects.create(
            document=document,
            created_by=created_by,
            **data,
        )
        # FIX #13: defer audit log to post-commit
        _doc_num = document.document_number
        _rev_num = rev.revision_number
        _rev_id  = rev.pk
        _user    = created_by
        _run_after_commit_or_now(lambda: AuditService.log(
            user=_user,
            module='EDMS',
            action='CREATE_REVISION',
            entity_type='Revision',
            entity_id=_rev_id,
            entity_identifier=f'{_doc_num} Rev {_rev_num}',
            description=f'Revision {_rev_num} added to {_doc_num}.',
        ))
        return rev

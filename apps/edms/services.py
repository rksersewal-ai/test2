"""EDMS business-logic / service layer.

Keeps views thin and orchestrates cross-cutting actions
(audit logging, status transitions, revision numbering).
"""
from django.db import transaction
from apps.edms.models import Document, Revision, FileAttachment
from apps.audit.services import AuditService


class DocumentService:
    @staticmethod
    @transaction.atomic
    def create_document(data: dict, created_by) -> Document:
        doc = Document.objects.create(created_by=created_by, **data)
        AuditService.log(
            user=created_by,
            module='EDMS',
            action='CREATE_DOCUMENT',
            entity_type='Document',
            entity_id=doc.pk,
            entity_identifier=doc.document_number,
            description=f'Document {doc.document_number} created.',
        )
        return doc

    @staticmethod
    @transaction.atomic
    def update_status(doc: Document, new_status: str, user) -> Document:
        old_status = doc.status
        doc.status = new_status
        doc.save(update_fields=['status', 'updated_at'])
        AuditService.log(
            user=user,
            module='EDMS',
            action='UPDATE_STATUS',
            entity_type='Document',
            entity_id=doc.pk,
            entity_identifier=doc.document_number,
            description=f'Status changed {old_status} → {new_status}.',
        )
        return doc

    @staticmethod
    def next_revision_number(document: Document) -> str:
        """Return the next revision label (00, 01, 02 …)."""
        count = document.revisions.count()
        return str(count).zfill(2)


class RevisionService:
    @staticmethod
    @transaction.atomic
    def create_revision(document: Document, data: dict, created_by) -> Revision:
        # Mark previous current revision as SUPERSEDED
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
        AuditService.log(
            user=created_by,
            module='EDMS',
            action='CREATE_REVISION',
            entity_type='Revision',
            entity_id=rev.pk,
            entity_identifier=f'{document.document_number} Rev {rev.revision_number}',
            description=f'Revision {rev.revision_number} added to {document.document_number}.',
        )
        return rev

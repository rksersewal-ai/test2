import pytest
from apps.edms.services import DocumentService
from apps.audit.models import AuditLog
from tests.factories import UserFactory, SectionFactory

@pytest.mark.django_db
class TestDocumentService:
    def test_create_document_success(self):
        user = UserFactory.create()
        section = SectionFactory.create()
        data = {
            'document_number': 'PLW/TEST/2026/0001',
            'title': 'Test Document',
            'doc_type_id': None,  # Optional in model
            'status': 'DRAFT',
            'section': section,
        }

        doc = DocumentService.create_document(data, user)

        # Verify Document creation
        assert doc.pk is not None
        assert doc.document_number == data['document_number']
        assert doc.title == data['title']
        assert doc.created_by == user
        assert doc.section == section

        # Verify AuditLog entry
        audit_log = AuditLog.objects.filter(
            entity_type='Document',
            entity_id=doc.pk
        ).first()

        assert audit_log is not None
        assert audit_log.user == user
        assert audit_log.module == 'EDMS'
        assert audit_log.action == 'CREATE_DOCUMENT'
        assert audit_log.entity_identifier == doc.document_number
        assert f'Document {doc.document_number} created.' in audit_log.description

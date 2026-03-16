# =============================================================================
# FILE: tests/test_phase1_integration.py
# Phase 1 Integration Tests — FR-001 through FR-006
# End-to-end flow: Upload → OCR → Metadata auto-fill → Version create
# Validates PRD Phase 1 success criteria (Week 4 deliverable).
# =============================================================================
import pytest
from io import BytesIO
from django.core.files.uploadedfile import InMemoryUploadedFile
from apps.edms.models import Document
from apps.metadata.models import MetadataField
from apps.metadata.services import MetadataService
from apps.versioning.services import VersioningService
from tests.factories import UserFactory, DocumentFactory, DocumentTypeFactory


def make_pdf(content: bytes = b'%PDF-1.4 test content') -> InMemoryUploadedFile:
    buf = BytesIO(content)
    return InMemoryUploadedFile(buf, 'file', 'doc.pdf', 'application/pdf', len(content), None)


@pytest.mark.django_db
class TestPhase1EndToEnd:

    def test_document_upload_metadata_version_flow(self):
        """Full Phase 1 flow: create document → set metadata → create version."""
        user     = UserFactory()
        doc_type = DocumentTypeFactory()
        document = DocumentFactory(document_type=doc_type)

        # FR-005: Setup metadata fields
        field_invoice = MetadataField.objects.create(
            document_type=doc_type, field_name='invoice_no',
            field_label='Invoice Number', field_type='text', is_required=True
        )
        field_amount = MetadataField.objects.create(
            document_type=doc_type, field_name='amount',
            field_label='Amount (INR)', field_type='number'
        )

        # FR-005: Set metadata values
        MetadataService.set_value(document, field_invoice, 'INV-2026-PLW-001', user=user)
        MetadataService.set_value(document, field_amount, '150000', user=user)

        assert document.metadata_values.count() == 2

        # FR-005: Simulate OCR auto-fill
        MetadataService.auto_fill_from_ocr(
            document, {'invoice_no': 'INV-2026-PLW-001-OCR'}, user=user
        )
        from apps.metadata.models import MetadataHistory
        assert MetadataHistory.objects.filter(metadata__document=document).count() == 1

        # FR-006: Create first version
        v1 = VersioningService.create_version(
            document, make_pdf(b'%PDF v1'), 'Initial upload', user=user
        )
        assert v1.version_number == '1.0'
        assert len(v1.checksum_sha256) == 64

        # FR-006: Create second version
        v2 = VersioningService.create_version(
            document, make_pdf(b'%PDF v2 corrected'), 'Correction pass 1', user=user
        )
        assert v2.version_number == '1.1'

        # FR-006: Rollback to v1.0
        rolled = VersioningService.rollback(document, '1.0', user=user, reason='v1.1 had error')
        assert rolled.version_number == '1.2'

        # FR-005: Export metadata
        csv_out  = MetadataService.export_csv(document)
        json_out = MetadataService.export_json(document)
        assert 'Invoice Number' in csv_out
        assert 'invoice_no' in json_out

    def test_metadata_export_accuracy_100_percent(self):
        """PRD KPI: 100% metadata accuracy — exported values match stored values."""
        import json
        user     = UserFactory()
        doc_type = DocumentTypeFactory()
        document = DocumentFactory(document_type=doc_type)
        field = MetadataField.objects.create(
            document_type=doc_type, field_name='drawing_no',
            field_label='Drawing Number', field_type='text'
        )
        MetadataService.set_value(document, field, 'DRG-WAG9-001', user=user)
        data = json.loads(MetadataService.export_json(document))
        assert data[0]['value'] == 'DRG-WAG9-001'

    def test_version_integrity_checksum(self):
        """PRD KPI: 100% version integrity — same file produces same checksum."""
        user     = UserFactory()
        document = DocumentFactory()
        content  = b'%PDF deterministic content'
        v1 = VersioningService.create_version(document, make_pdf(content), 'v1', user)

        import hashlib
        expected = hashlib.sha256(content).hexdigest()
        assert v1.checksum_sha256 == expected

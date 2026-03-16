# =============================================================================
# FILE: tests/test_phase1_integration.py
# Phase 1 E2E Integration Tests — Amended PRD v1.0
# Flow: Document → Metadata auto-fill from OCR → Version create with
#       alteration history → Rollback → Export CSV/JSON
# PRD KPIs tested:
#   - 100% metadata export accuracy
#   - SHA-256 version integrity
#   - Alteration history per PRD Table 13.9
# =============================================================================
import pytest
import json
import hashlib
from io import BytesIO
from django.core.files.uploadedfile import InMemoryUploadedFile
from apps.metadata.models import MetadataField, MetadataHistory
from apps.metadata.services import MetadataService
from apps.versioning.models import AlterationHistory, DocumentVersion
from apps.versioning.services import VersioningService
from tests.factories import UserFactory, DocumentFactory, DocumentTypeFactory


def make_pdf(content: bytes = b'%PDF-1.4 test') -> InMemoryUploadedFile:
    buf = BytesIO(content)
    return InMemoryUploadedFile(buf, 'file', 'doc.pdf', 'application/pdf', len(content), None)


@pytest.mark.django_db
class TestPhase1FullFlow:

    def test_upload_metadata_version_rollback_export(self):
        """Full Phase 1 E2E flow as defined in amended PRD."""
        user     = UserFactory()
        doc_type = DocumentTypeFactory()
        document = DocumentFactory(document_type=doc_type)

        # FR-005: Setup metadata fields (PRD 5.2.3)
        field_drg = MetadataField.objects.create(
            document_type=doc_type, field_name='drawing_no',
            field_label='Drawing Number', field_type='text', is_required=True
        )
        field_ctrl = MetadataField.objects.create(
            document_type=doc_type, field_name='controlling_agency',
            field_label='Controlling Agency', field_type='select',
            select_options='CLW, BLW, RDSO, ICF, PLW'
        )
        field_cat = MetadataField.objects.create(
            document_type=doc_type, field_name='inspection_category',
            field_label='Inspection Category', field_type='select',
            select_options='CAT-A, CAT-B, CAT-C, CAT-D'
        )

        # Set metadata values
        MetadataService.set_value(document, field_drg, 'CLW/ED/C/WAG9-54321', user=user)
        MetadataService.set_value(document, field_ctrl, 'CLW', user=user)
        MetadataService.set_value(document, field_cat, 'CAT-A', user=user)
        assert document.metadata_values.count() == 3

        # FR-005: OCR auto-fill simulation (drawing number found by OCR)
        MetadataService.auto_fill_from_ocr(
            document, {'drawing_no': 'CLW/ED/C/WAG9-54321-OCR'}, user=user
        )
        assert MetadataHistory.objects.filter(metadata__document=document).count() == 1

        # FR-006: Create version v1.0 with alteration history (PRD 7.3 / Table 13.9)
        v1 = VersioningService.create_version(
            document, make_pdf(b'%PDF v1'),
            edit_summary='Initial release',
            user=user,
            alteration_number='00',
            source_agency='CLW',
            change_reason='Initial issue',
        )
        assert v1.version_number == '1.0'
        assert len(v1.checksum_sha256) == 64
        assert AlterationHistory.objects.filter(
            document=document, alteration_number='00'
        ).exists()

        # FR-006: Version v1.1 with alteration 01
        v2 = VersioningService.create_version(
            document, make_pdf(b'%PDF v2 corrections'),
            edit_summary='Tolerance correction per RDSO letter',
            user=user,
            alteration_number='01',
            source_agency='RDSO',
            change_reason='Tolerance updated',
            probable_impacts='Affects sub-assembly A'
        )
        assert v2.version_number == '1.1'
        v1.refresh_from_db()
        assert v1.status == DocumentVersion.VersionStatus.PREVIOUS

        # FR-006: Rollback to v1.0 (PRD 5.2.4)
        rolled = VersioningService.rollback(
            document, '1.0', user=user, reason='v1.1 introduced dimension error'
        )
        assert rolled.version_number == '1.2'

        # FR-005: Export accuracy check (PRD KPI: 100% metadata accuracy)
        csv_out  = MetadataService.export_csv(document)
        json_out = json.loads(MetadataService.export_json(document))
        assert 'Drawing Number' in csv_out
        assert any(d['field_name'] == 'controlling_agency' for d in json_out)

    def test_sha256_deterministic(self):
        """PRD KPI: 100% version integrity — same file always same checksum."""
        user    = UserFactory()
        doc     = DocumentFactory()
        content = b'%PDF deterministic'
        v1 = VersioningService.create_version(doc, make_pdf(content), 'v1', user)
        assert v1.checksum_sha256 == hashlib.sha256(content).hexdigest()

    def test_alteration_history_full_record(self):
        """PRD Table 13.9: Verify all key alteration fields are stored."""
        user = UserFactory()
        doc  = DocumentFactory()
        VersioningService.create_version(
            doc, make_pdf(b'v1'),
            edit_summary='Material spec updated',
            user=user,
            alteration_number='02',
            source_agency='CLW',
            change_reason='BIS standard updated',
            probable_impacts='Affects material procurement'
        )
        alt = AlterationHistory.objects.get(document=doc, alteration_number='02')
        assert alt.source_agency  == 'CLW'
        assert alt.change_reason  == 'BIS standard updated'
        assert alt.probable_impacts == 'Affects material procurement'
        assert alt.implementation_status == AlterationHistory.ImplementationStatus.IMPLEMENTED

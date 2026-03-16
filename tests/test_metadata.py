# =============================================================================
# FILE: tests/test_metadata.py
# FR-005: Unit tests for Metadata Management
# Covers: MetadataField CRUD, set/bulk-set/auto-fill,
#         MetadataHistory recording, CSV/JSON export.
# =============================================================================
import pytest
from django.contrib.auth import get_user_model
from apps.edms.models import Document, DocumentType
from apps.metadata.models import MetadataField, DocumentMetadata, MetadataHistory
from apps.metadata.services import MetadataService
from tests.factories import UserFactory, DocumentFactory, DocumentTypeFactory

User = get_user_model()


@pytest.mark.django_db
class TestMetadataField:

    def test_create_text_field(self):
        doc_type = DocumentTypeFactory()
        field    = MetadataField.objects.create(
            document_type=doc_type, field_name='vendor_name',
            field_label='Vendor Name', field_type=MetadataField.FieldType.TEXT,
            is_required=True,
        )
        assert field.pk is not None
        assert field.is_required is True

    def test_select_options_list(self):
        doc_type = DocumentTypeFactory()
        field    = MetadataField.objects.create(
            document_type=doc_type, field_name='currency',
            field_label='Currency', field_type=MetadataField.FieldType.SELECT,
            select_options='INR, USD, EUR',
        )
        options = field.get_select_options_list()
        assert 'INR' in options
        assert len(options) == 3

    def test_unique_field_name_per_doc_type(self):
        from django.db import IntegrityError
        doc_type = DocumentTypeFactory()
        MetadataField.objects.create(
            document_type=doc_type, field_name='ref_no',
            field_label='Reference Number', field_type='text'
        )
        with pytest.raises(IntegrityError):
            MetadataField.objects.create(
                document_type=doc_type, field_name='ref_no',
                field_label='Duplicate', field_type='text'
            )


@pytest.mark.django_db
class TestMetadataService:

    def setup_method(self):
        self.user     = UserFactory()
        self.doc_type = DocumentTypeFactory()
        self.document = DocumentFactory(document_type=self.doc_type)
        self.field    = MetadataField.objects.create(
            document_type=self.doc_type, field_name='invoice_number',
            field_label='Invoice Number', field_type='text',
        )

    def test_set_value_creates_record(self):
        meta = MetadataService.set_value(
            self.document, self.field, 'INV-2026-001', user=self.user
        )
        assert meta.pk is not None
        assert meta.value == 'INV-2026-001'
        assert meta.auto_filled is False

    def test_update_records_history(self):
        MetadataService.set_value(self.document, self.field, 'INV-001', user=self.user)
        MetadataService.set_value(self.document, self.field, 'INV-002', user=self.user)
        history = MetadataHistory.objects.filter(metadata__document=self.document)
        assert history.count() == 1
        assert history.first().old_value == 'INV-001'
        assert history.first().new_value == 'INV-002'

    def test_same_value_no_history(self):
        MetadataService.set_value(self.document, self.field, 'INV-001', user=self.user)
        MetadataService.set_value(self.document, self.field, 'INV-001', user=self.user)
        assert MetadataHistory.objects.filter(metadata__document=self.document).count() == 0

    def test_bulk_set(self):
        MetadataField.objects.create(
            document_type=self.doc_type, field_name='amount',
            field_label='Amount', field_type='number'
        )
        results = MetadataService.bulk_set(
            self.document,
            {'invoice_number': 'INV-2026-005', 'amount': '50000'},
            user=self.user
        )
        assert len(results) == 2

    def test_auto_fill_flag(self):
        meta = MetadataService.set_value(
            self.document, self.field, 'OCR-INV-001', user=self.user, auto_filled=True
        )
        assert meta.auto_filled is True

    def test_export_csv_contains_header_and_value(self):
        MetadataService.set_value(self.document, self.field, 'INV-CSV-001', user=self.user)
        csv_out = MetadataService.export_csv(self.document)
        assert 'Invoice Number' in csv_out
        assert 'INV-CSV-001' in csv_out

    def test_export_json_structure(self):
        import json
        MetadataService.set_value(self.document, self.field, 'INV-JSON-001', user=self.user)
        data = json.loads(MetadataService.export_json(self.document))
        assert any(d['value'] == 'INV-JSON-001' for d in data)
        assert 'field_name' in data[0]

    def test_get_history_filtered_by_field(self):
        MetadataService.set_value(self.document, self.field, 'A', user=self.user)
        MetadataService.set_value(self.document, self.field, 'B', user=self.user)
        history = MetadataService.get_history(self.document, field_name='invoice_number')
        assert history.count() == 1

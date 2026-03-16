# =============================================================================
# FILE: apps/metadata/services.py
# FR-005: Business logic for metadata management
# Handles bulk set, auto-fill from OCR, CSV/JSON export,
# history recording, and metadata search.
# =============================================================================
import csv
import json
from io import StringIO
from django.db import transaction
from apps.edms.models import Document
from .models import MetadataField, DocumentMetadata, MetadataHistory


class MetadataService:

    @staticmethod
    @transaction.atomic
    def set_value(document: Document, field: MetadataField,
                  new_value: str, user=None,
                  auto_filled: bool = False,
                  change_note: str = '') -> DocumentMetadata:
        """Create or update a metadata value, recording history on change."""
        obj, created = DocumentMetadata.objects.get_or_create(
            document=document,
            field=field,
            defaults={'value': new_value, 'auto_filled': auto_filled, 'updated_by': user}
        )
        if not created and obj.value != new_value:
            MetadataHistory.objects.create(
                metadata=obj,
                old_value=obj.value,
                new_value=new_value,
                changed_by=user,
                change_note=change_note,
            )
            obj.value       = new_value
            obj.auto_filled = auto_filled
            obj.updated_by  = user
            obj.save(update_fields=['value', 'auto_filled', 'updated_by', 'updated_at'])
        return obj

    @staticmethod
    def bulk_set(document: Document, field_value_map: dict,
                 user=None, auto_filled: bool = False) -> list:
        """Set multiple metadata values at once.
        field_value_map = {field_name: value}
        """
        results = []
        if not document.document_type:
            return results
        fields = MetadataField.objects.filter(
            document_type=document.document_type,
            field_name__in=field_value_map.keys(),
            is_active=True
        )
        for field in fields:
            val = field_value_map.get(field.field_name, '')
            results.append(
                MetadataService.set_value(document, field, str(val), user, auto_filled)
            )
        return results

    @staticmethod
    def auto_fill_from_ocr(document: Document, ocr_data: dict, user=None):
        """Auto-fill metadata from OCR-extracted key-value pairs."""
        return MetadataService.bulk_set(document, ocr_data, user=user, auto_filled=True)

    @staticmethod
    def export_csv(document: Document) -> str:
        """Export document metadata as CSV string (PRD: Export to Excel/CSV support)."""
        values = DocumentMetadata.objects.filter(
            document=document, field__is_exportable=True
        ).select_related('field')
        output = StringIO()
        writer = csv.writer(output)
        writer.writerow(['Field', 'Value', 'Auto Filled', 'Last Updated'])
        for v in values:
            writer.writerow([v.field.field_label, v.value, v.auto_filled, v.updated_at])
        return output.getvalue()

    @staticmethod
    def export_json(document: Document) -> str:
        """Export document metadata as JSON string."""
        values = DocumentMetadata.objects.filter(
            document=document, field__is_exportable=True
        ).select_related('field')
        data = [
            {
                'field':        v.field.field_label,
                'field_name':   v.field.field_name,
                'value':        v.value,
                'auto_filled':  v.auto_filled,
                'updated_at':   str(v.updated_at),
            }
            for v in values
        ]
        return json.dumps(data, indent=2)

    @staticmethod
    def get_history(document: Document, field_name: str = None):
        """Return metadata change history for a document."""
        qs = MetadataHistory.objects.filter(
            metadata__document=document
        ).select_related('metadata__field', 'changed_by').order_by('-changed_at')
        if field_name:
            qs = qs.filter(metadata__field__field_name=field_name)
        return qs

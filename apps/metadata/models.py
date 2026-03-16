# =============================================================================
# FILE: apps/metadata/models.py
# FR-005: Metadata Management
# Amended PRD v1.0 — PLW LDO Digital Management System
# Covers: MetadataField definitions, DocumentMetadata values,
#         MetadataHistory audit trail, auto-fill from OCR.
# Tables: meta_field, meta_document_value, meta_history
# =============================================================================
from django.db import models
from django.conf import settings
from apps.edms.models import Document, DocumentType


class MetadataField(models.Model):
    """Custom metadata field definition per DocumentType."""

    class FieldType(models.TextChoices):
        TEXT     = 'text',     'Text'
        NUMBER   = 'number',   'Number'
        DATE     = 'date',     'Date'
        BOOLEAN  = 'boolean',  'Yes / No'
        SELECT   = 'select',   'Select (Dropdown)'
        TEXTAREA = 'textarea', 'Long Text'

    document_type    = models.ForeignKey(DocumentType, on_delete=models.CASCADE,
                                         related_name='metadata_fields')
    field_name       = models.CharField(max_length=80)
    field_label      = models.CharField(max_length=200)
    field_type       = models.CharField(max_length=20, choices=FieldType.choices,
                                        default=FieldType.TEXT)
    select_options   = models.TextField(blank=True,
                                        help_text='Comma-separated values for SELECT type')
    is_required      = models.BooleanField(default=False)
    is_searchable    = models.BooleanField(default=True)
    is_exportable    = models.BooleanField(default=True)
    default_value    = models.CharField(max_length=500, blank=True)
    validation_regex = models.CharField(max_length=300, blank=True)
    sort_order       = models.IntegerField(default=0)
    is_active        = models.BooleanField(default=True)
    created_by       = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True,
                                         on_delete=models.SET_NULL,
                                         related_name='metadata_fields_created')
    created_at       = models.DateTimeField(auto_now_add=True)
    updated_at       = models.DateTimeField(auto_now=True)

    class Meta:
        db_table        = 'meta_field'
        unique_together = [('document_type', 'field_name')]
        ordering        = ['document_type', 'sort_order', 'field_name']

    def __str__(self):
        return f"{self.document_type.name} / {self.field_label} [{self.field_type}]"

    def get_select_options_list(self) -> list:
        if self.field_type == self.FieldType.SELECT and self.select_options:
            return [o.strip() for o in self.select_options.split(',') if o.strip()]
        return []


class DocumentMetadata(models.Model):
    """Stores a metadata field value for a specific document."""

    document    = models.ForeignKey(Document, on_delete=models.CASCADE,
                                    related_name='metadata_values')
    field       = models.ForeignKey(MetadataField, on_delete=models.RESTRICT,
                                    related_name='values')
    value       = models.TextField(blank=True, null=True)
    auto_filled = models.BooleanField(default=False,
                                      help_text='True if populated by OCR/AI auto-fill')
    updated_by  = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True,
                                    on_delete=models.SET_NULL,
                                    related_name='metadata_updated')
    updated_at  = models.DateTimeField(auto_now=True)

    class Meta:
        db_table        = 'meta_document_value'
        unique_together = [('document', 'field')]
        ordering        = ['field__sort_order']

    def __str__(self):
        return f"{self.document.document_number} | {self.field.field_label} = {self.value}"


class MetadataHistory(models.Model):
    """Immutable audit trail of every change to a document metadata value."""

    metadata    = models.ForeignKey(DocumentMetadata, on_delete=models.CASCADE,
                                    related_name='history')
    old_value   = models.TextField(blank=True, null=True)
    new_value   = models.TextField(blank=True, null=True)
    changed_by  = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True,
                                    on_delete=models.SET_NULL,
                                    related_name='metadata_history')
    changed_at  = models.DateTimeField(auto_now_add=True)
    change_note = models.CharField(max_length=300, blank=True)

    class Meta:
        db_table = 'meta_history'
        ordering = ['-changed_at']

    def __str__(self):
        return (
            f"{self.metadata.document.document_number} / "
            f"{self.metadata.field.field_label}: ’{self.old_value}’ → ’{self.new_value}’"
        )

from django.contrib import admin
from .models import MetadataField, DocumentMetadata, MetadataHistory


@admin.register(MetadataField)
class MetadataFieldAdmin(admin.ModelAdmin):
    list_display   = ['field_label', 'document_type', 'field_type', 'is_required', 'is_active', 'sort_order']
    list_filter    = ['document_type', 'field_type', 'is_required', 'is_active']
    search_fields  = ['field_name', 'field_label']
    ordering       = ['document_type', 'sort_order']


@admin.register(DocumentMetadata)
class DocumentMetadataAdmin(admin.ModelAdmin):
    list_display   = ['document', 'field', 'value', 'auto_filled', 'updated_at']
    list_filter    = ['auto_filled', 'field__document_type']
    search_fields  = ['document__document_number', 'field__field_label', 'value']
    raw_id_fields  = ['document', 'field']


@admin.register(MetadataHistory)
class MetadataHistoryAdmin(admin.ModelAdmin):
    list_display    = ['metadata', 'old_value', 'new_value', 'changed_by', 'changed_at']
    readonly_fields = ['changed_at']
    search_fields   = ['metadata__document__document_number', 'metadata__field__field_label']

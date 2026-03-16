# =============================================================================
# FILE: apps/metadata/serializers.py
# FR-005: REST serializers for MetadataField, DocumentMetadata, MetadataHistory
# =============================================================================
from rest_framework import serializers
from .models import MetadataField, DocumentMetadata, MetadataHistory


class MetadataFieldSerializer(serializers.ModelSerializer):
    select_options_list = serializers.SerializerMethodField()

    class Meta:
        model  = MetadataField
        fields = [
            'id', 'document_type', 'field_name', 'field_label', 'field_type',
            'select_options', 'select_options_list', 'is_required', 'is_searchable',
            'is_exportable', 'default_value', 'validation_regex',
            'sort_order', 'is_active', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'select_options_list']

    def get_select_options_list(self, obj):
        return obj.get_select_options_list()


class DocumentMetadataSerializer(serializers.ModelSerializer):
    field_label = serializers.CharField(source='field.field_label', read_only=True)
    field_type  = serializers.CharField(source='field.field_type',  read_only=True)

    class Meta:
        model  = DocumentMetadata
        fields = [
            'id', 'document', 'field', 'field_label', 'field_type',
            'value', 'auto_filled', 'updated_by', 'updated_at',
        ]
        read_only_fields = ['id', 'field_label', 'field_type', 'updated_at']


class MetadataHistorySerializer(serializers.ModelSerializer):
    changed_by_username = serializers.CharField(
        source='changed_by.username', read_only=True, default='system'
    )

    class Meta:
        model  = MetadataHistory
        fields = ['id', 'metadata', 'old_value', 'new_value',
                  'changed_by', 'changed_by_username', 'changed_at', 'change_note']
        read_only_fields = ['id', 'changed_at', 'changed_by_username']

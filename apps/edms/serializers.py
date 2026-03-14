# =============================================================================
# FILE: apps/edms/serializers.py
# SPRINT 1 additions:
#   - CustomFieldDefinitionSerializer  (Feature #9)
#   - DocumentCustomFieldSerializer    (Feature #9)
#   - BulkUpsertCustomFieldsSerializer (Feature #9 — bulk save all fields at once)
#   - CorrespondentSerializer          (Feature #14)
#   - DocumentCorrespondentLinkSerializer (Feature #14)
#   - DocumentNoteSerializer           (Feature #12)
#   - ResolveNoteSerializer            (Feature #12)
# All previous serializers preserved.
# =============================================================================
from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.utils import timezone

from apps.edms.models import (
    Document, Revision, FileAttachment, Category, DocumentType,
    CustomFieldDefinition, DocumentCustomField,
    Correspondent, DocumentCorrespondentLink,
    DocumentNote,
)
from apps.edms.validators import validate_file_upload

User = get_user_model()


# ---------------------------------------------------------------------------
# Existing serializers (unchanged)
# ---------------------------------------------------------------------------

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model  = Category
        fields = ['id', 'code', 'name', 'description', 'parent', 'is_active']


class DocumentTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model  = DocumentType
        fields = ['id', 'code', 'name', 'description', 'is_active']


class DocumentListSerializer(serializers.ModelSerializer):
    category_name      = serializers.CharField(source='category.name', read_only=True)
    document_type_name = serializers.CharField(source='document_type.name', read_only=True)
    section_name       = serializers.CharField(source='section.name', read_only=True)

    class Meta:
        model  = Document
        fields = [
            'id', 'document_number', 'title', 'status',
            'category_name', 'document_type_name', 'section_name',
            'source_standard', 'eoffice_file_number', 'created_at', 'updated_at',
        ]


class DocumentDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model       = Document
        fields      = '__all__'
        read_only_fields = ['created_by', 'created_at', 'updated_at']


class RevisionSerializer(serializers.ModelSerializer):
    prepared_by_name = serializers.SerializerMethodField(read_only=True)
    approved_by_name = serializers.SerializerMethodField(read_only=True)
    prepared_by_id   = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.filter(is_active=True),
        source='prepared_by', write_only=True, required=False, allow_null=True
    )
    approved_by_id   = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.filter(is_active=True),
        source='approved_by', write_only=True, required=False, allow_null=True
    )

    def get_prepared_by_name(self, obj):
        return obj.prepared_by.get_full_name() if obj.prepared_by else ''

    def get_approved_by_name(self, obj):
        return obj.approved_by.get_full_name() if obj.approved_by else ''

    class Meta:
        model  = Revision
        fields = [
            'id', 'document', 'revision_number', 'revision_date', 'status',
            'change_description', 'prepared_by_id', 'prepared_by_name',
            'approved_by_id', 'approved_by_name',
            'eoffice_ref', 'created_by', 'created_at', 'updated_at',
        ]
        read_only_fields = ['created_by', 'created_at', 'updated_at']


class FileAttachmentSerializer(serializers.ModelSerializer):
    file = serializers.FileField(write_only=True)

    class Meta:
        model  = FileAttachment
        fields = [
            'id', 'revision', 'file', 'file_name', 'file_path',
            'file_size_bytes', 'file_type', 'page_count',
            'checksum_sha256', 'is_primary', 'uploaded_by', 'uploaded_at',
        ]
        read_only_fields = [
            'file_path', 'file_size_bytes', 'checksum_sha256',
            'uploaded_by', 'uploaded_at', 'file_name',
        ]

    def validate_file(self, file_obj):
        checksum = validate_file_upload(file_obj)
        self._validated_checksum = checksum
        return file_obj

    def create(self, validated_data):
        file_obj = validated_data.pop('file')
        validated_data['file_name']       = file_obj.name
        validated_data['file_size_bytes'] = file_obj.size
        validated_data['checksum_sha256'] = getattr(self, '_validated_checksum', '')
        validated_data['uploaded_by']     = self.context['request'].user
        attachment = FileAttachment(**validated_data)
        attachment.file_path = file_obj
        attachment.save()
        return attachment


# ---------------------------------------------------------------------------
# SPRINT 1 — Feature #9: Custom Fields
# ---------------------------------------------------------------------------

class CustomFieldDefinitionSerializer(serializers.ModelSerializer):
    select_options_list = serializers.SerializerMethodField(read_only=True)
    document_type_name  = serializers.CharField(source='document_type.name', read_only=True)

    def get_select_options_list(self, obj):
        return obj.get_select_options_list()

    class Meta:
        model  = CustomFieldDefinition
        fields = [
            'id', 'document_type', 'document_type_name',
            'field_name', 'field_label', 'field_type',
            'select_options', 'select_options_list',
            'is_required', 'sort_order', 'is_active', 'created_at',
        ]
        read_only_fields = ['created_at']


class DocumentCustomFieldSerializer(serializers.ModelSerializer):
    field_label     = serializers.CharField(source='definition.field_label', read_only=True)
    field_type      = serializers.CharField(source='definition.field_type',  read_only=True)
    field_name      = serializers.CharField(source='definition.field_name',  read_only=True)
    is_required     = serializers.BooleanField(source='definition.is_required', read_only=True)
    updated_by_name = serializers.SerializerMethodField(read_only=True)

    def get_updated_by_name(self, obj):
        return obj.updated_by.get_full_name() if obj.updated_by else ''

    class Meta:
        model  = DocumentCustomField
        fields = [
            'id', 'document', 'definition', 'field_name', 'field_label',
            'field_type', 'is_required', 'field_value',
            'updated_by_name', 'updated_at',
        ]
        read_only_fields = ['updated_at']


class BulkUpsertCustomFieldsSerializer(serializers.Serializer):
    """Accept a list of {definition_id, field_value} to bulk-save all custom
    fields for a document in a single POST instead of N separate PATCH calls.
    """
    fields = serializers.ListField(
        child=serializers.DictField(child=serializers.CharField(allow_blank=True)),
        allow_empty=True
    )

    def validate_fields(self, value):
        for item in value:
            if 'definition_id' not in item:
                raise serializers.ValidationError('Each item must have definition_id.')
        return value


# ---------------------------------------------------------------------------
# SPRINT 1 — Feature #14: Correspondent Tracking
# ---------------------------------------------------------------------------

class CorrespondentSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Correspondent
        fields = [
            'id', 'name', 'short_code', 'org_type',
            'address', 'email', 'is_active', 'created_at',
        ]
        read_only_fields = ['created_at']


class DocumentCorrespondentLinkSerializer(serializers.ModelSerializer):
    correspondent_name      = serializers.CharField(source='correspondent.name',       read_only=True)
    correspondent_short_code = serializers.CharField(source='correspondent.short_code', read_only=True)
    correspondent_org_type  = serializers.CharField(source='correspondent.org_type',   read_only=True)
    created_by_name         = serializers.SerializerMethodField(read_only=True)

    def get_created_by_name(self, obj):
        return obj.created_by.get_full_name() if obj.created_by else ''

    class Meta:
        model  = DocumentCorrespondentLink
        fields = [
            'id', 'document', 'correspondent', 'correspondent_name',
            'correspondent_short_code', 'correspondent_org_type',
            'reference_number', 'reference_date', 'link_type',
            'remarks', 'created_by_name', 'created_at',
        ]
        read_only_fields = ['created_at']


# ---------------------------------------------------------------------------
# SPRINT 1 — Feature #12: Document Notes
# ---------------------------------------------------------------------------

class DocumentNoteSerializer(serializers.ModelSerializer):
    created_by_name  = serializers.SerializerMethodField(read_only=True)
    resolved_by_name = serializers.SerializerMethodField(read_only=True)

    def get_created_by_name(self, obj):
        return obj.created_by.get_full_name() if obj.created_by else ''

    def get_resolved_by_name(self, obj):
        return obj.resolved_by.get_full_name() if obj.resolved_by else ''

    class Meta:
        model  = DocumentNote
        fields = [
            'id', 'document', 'revision', 'note_type', 'note_text',
            'is_resolved', 'resolved_by', 'resolved_by_name',
            'resolved_at', 'resolution_note',
            'created_by', 'created_by_name', 'created_at', 'updated_at',
        ]
        read_only_fields = [
            'is_resolved', 'resolved_by', 'resolved_at',
            'created_by', 'created_at', 'updated_at',
        ]


class ResolveNoteSerializer(serializers.Serializer):
    """Used by PATCH /notes/{id}/resolve/ — only accepts resolution_note."""
    resolution_note = serializers.CharField(required=False, allow_blank=True, default='')

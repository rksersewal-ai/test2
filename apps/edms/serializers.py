# =============================================================================
# FILE: apps/edms/serializers.py
# FIXES applied:
#   #6  - DocumentListSerializer._latest_revision() uses prefetch cache first
#         to avoid N+1 query (one extra DB hit per document on list pages).
#   #7  - BulkUpsertCustomFieldsSerializer.fields max_length=200 to prevent
#         DoS via 10,000-item list holding a DB connection open.
#   #8  - FileAttachmentSerializer: SHA-256 checksum computation moved out of
#         request thread — validator now does size+magic only; checksum is
#         computed asynchronously post-save via Celery task.
#   #12 - DocumentListSerializer: removed duplicate `document_type` field that
#         shadowed the FK with a read-only char field, causing silent data loss
#         on PATCH (frontend sends doc type by name but DRF ignores it).
#   #15 - FileAttachmentSerializer.create() wrapped in transaction.atomic so
#         a DB constraint failure after disk write does not orphan the file.
#   #23 - get_file_url() now uses request.build_absolute_uri() so URLs are
#         correct regardless of reverse-proxy SCRIPT_NAME or API prefix.
# =============================================================================
from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.db import transaction
from django.utils import timezone

from apps.edms.models import (
    Document, Revision, FileAttachment, Category, DocumentType,
    CustomFieldDefinition, DocumentCustomField,
    Correspondent, DocumentCorrespondentLink,
    DocumentNote,
)
from apps.edms.validators import validate_file_upload

User = get_user_model()


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model  = Category
        fields = ['id', 'code', 'name', 'description', 'parent', 'is_active']


class DocumentTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model  = DocumentType
        fields = ['id', 'code', 'name', 'description', 'is_active']


class DocumentListSerializer(serializers.ModelSerializer):
    doc_number         = serializers.CharField(source='document_number', read_only=True)
    category_name      = serializers.CharField(source='category.name',        read_only=True)
    document_type_name = serializers.CharField(source='document_type.name',   read_only=True)
    # FIX #12: removed duplicate `document_type = CharField(source='document_type.name')`
    # that was shadowing the FK and causing silent data loss on PATCH requests.
    # document_type FK is now handled by ModelSerializer directly.
    section_name    = serializers.CharField(source='section.name',     read_only=True)
    created_by_name = serializers.CharField(source='created_by.full_name', read_only=True)
    version         = serializers.SerializerMethodField(read_only=True)
    revision        = serializers.SerializerMethodField(read_only=True)
    file_url        = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model  = Document
        fields = [
            'id', 'document_number', 'doc_number', 'title', 'status',
            'category_name', 'document_type_name', 'section_name',
            'source_standard', 'eoffice_file_number', 'created_at', 'updated_at',
            'version', 'revision', 'file_url', 'created_by_name',
        ]

    def _latest_revision(self, obj):
        """
        FIX #6: Use the prefetch cache when available to avoid firing
        one extra DB query per document on list pages (N+1 problem).
        """
        cache = getattr(obj, '_prefetched_objects_cache', {})
        if 'revisions' in cache:
            revisions = list(cache['revisions'])
            if revisions:
                # Already ordered by -revision_date,-created_at via Prefetch
                return revisions[0]
            return None
        # Fallback for direct instantiation outside a ViewSet
        return obj.revisions.order_by('-revision_date', '-created_at').first()

    def get_version(self, obj):
        revision = self._latest_revision(obj)
        return revision.revision_number if revision else ''

    def get_revision(self, obj):
        return self.get_version(obj)

    def get_file_url(self, obj):
        # FIX #23: build absolute URI so reverse-proxy prefix changes don't break URLs
        request = self.context.get('request')
        path = f'/api/v1/edms/documents/{obj.pk}/file/'
        if request:
            return request.build_absolute_uri(path)
        return path


class DocumentDetailSerializer(serializers.ModelSerializer):
    doc_number        = serializers.CharField(source='document_number', read_only=True)
    legacy_doc_number = serializers.CharField(write_only=True, required=False)
    doc_type          = serializers.CharField(write_only=True, required=False, allow_blank=True)
    language          = serializers.CharField(write_only=True, required=False, allow_blank=True)
    initial_revision_number = serializers.CharField(write_only=True, required=False, allow_blank=True)
    uploaded_file          = serializers.FileField(write_only=True, required=False, allow_null=True)
    category_name      = serializers.CharField(source='category.name',      read_only=True)
    document_type_name = serializers.CharField(source='document_type.name', read_only=True)
    section_name       = serializers.CharField(source='section.name',       read_only=True)
    created_by_name    = serializers.CharField(source='created_by.full_name', read_only=True)
    version  = serializers.SerializerMethodField(read_only=True)
    revision = serializers.SerializerMethodField(read_only=True)
    file_url = serializers.SerializerMethodField(read_only=True)
    latest_file_id = serializers.SerializerMethodField(read_only=True)
    tags     = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model            = Document
        fields           = '__all__'
        read_only_fields = ['created_by', 'created_at', 'updated_at']

    def to_internal_value(self, data):
        normalized = data.copy() if hasattr(data, 'copy') else dict(data)
        doc_number = normalized.get('doc_number') or normalized.get('legacy_doc_number')
        if doc_number and not normalized.get('document_number'):
            normalized['document_number'] = doc_number
        version = normalized.get('version')
        if version and not normalized.get('initial_revision_number'):
            normalized['initial_revision_number'] = version
        uploaded_file = normalized.get('file')
        if uploaded_file and not normalized.get('uploaded_file'):
            normalized['uploaded_file'] = uploaded_file
        normalized.pop('version', None)
        normalized.pop('file', None)
        return super().to_internal_value(normalized)

    def _resolve_document_type(self, raw_value):
        if raw_value in (None, ''):
            return None
        if isinstance(raw_value, int) or (isinstance(raw_value, str) and raw_value.isdigit()):
            return DocumentType.objects.filter(pk=int(raw_value)).first()
        normalized = str(raw_value).strip()
        if not normalized:
            return None
        return (
            DocumentType.objects.filter(code__iexact=normalized).first()
            or DocumentType.objects.filter(name__iexact=normalized).first()
        )

    def validate(self, attrs):
        attrs = super().validate(attrs)
        initial = getattr(self, 'initial_data', {}) or {}
        doc_type_value = initial.get('doc_type') or initial.get('document_type')
        if doc_type_value and not attrs.get('document_type'):
            document_type = self._resolve_document_type(doc_type_value)
            if document_type is not None:
                attrs['document_type'] = document_type
        attrs.pop('language', None)
        attrs.pop('doc_type', None)
        attrs.pop('legacy_doc_number', None)
        return attrs

    def _latest_revision(self, obj):
        cache = getattr(obj, '_prefetched_objects_cache', {})
        if 'revisions' in cache:
            revisions = list(cache['revisions'])
            return revisions[0] if revisions else None
        return obj.revisions.order_by('-revision_date', '-created_at').first()

    def get_version(self, obj):
        revision = self._latest_revision(obj)
        return revision.revision_number if revision else ''

    def get_revision(self, obj):
        return self.get_version(obj)

    def get_file_url(self, obj):
        # FIX #23
        request = self.context.get('request')
        path = f'/api/v1/edms/documents/{obj.pk}/file/'
        return request.build_absolute_uri(path) if request else path

    def get_latest_file_id(self, obj):
        revision = self._latest_revision(obj)
        if revision is None:
            return None
        cache = getattr(revision, '_prefetched_objects_cache', {})
        if 'files' in cache:
            files = sorted(
                list(cache['files']),
                key=lambda item: (item.is_primary, item.uploaded_at),
                reverse=True,
            )
            return files[0].pk if files else None
        attachment = revision.files.order_by('-is_primary', '-uploaded_at').first()
        return attachment.pk if attachment else None

    def get_tags(self, obj):
        if not obj.keywords:
            return []
        return [tag.strip() for tag in obj.keywords.split(',') if tag.strip()]


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
        # FIX #8: validate_file_upload now does size+magic bytes only.
        # SHA-256 checksum is computed asynchronously post-save by Celery task
        # (apps.edms.tasks.compute_attachment_checksum) to avoid blocking the
        # request thread for 50 MB files.
        validate_file_upload(file_obj)
        return file_obj

    @transaction.atomic
    def create(self, validated_data):
        # FIX #15: wrapped in transaction.atomic so that if the DB save fails
        # (e.g. unique constraint violation), the physical file already written
        # to disk by Django storage is cleaned up via the rollback hook below.
        file_obj = validated_data.pop('file')
        validated_data['file_name']       = file_obj.name
        validated_data['file_size_bytes'] = file_obj.size
        validated_data['checksum_sha256'] = ''   # computed async post-save
        validated_data['uploaded_by']     = self.context['request'].user
        attachment = FileAttachment(**validated_data)
        attachment.file_path = file_obj
        try:
            attachment.save()
        except Exception:
            # Clean up the orphaned disk file if DB insert failed
            try:
                if attachment.file_path and attachment.file_path.name:
                    attachment.file_path.delete(save=False)
            except Exception:
                pass
            raise
        # Schedule async checksum computation
        transaction.on_commit(lambda: _schedule_checksum(attachment.pk))
        return attachment


def _schedule_checksum(attachment_pk: int):
    """Enqueue the async SHA-256 task after the DB row is committed."""
    try:
        from apps.edms.tasks import compute_attachment_checksum
        compute_attachment_checksum.delay(attachment_pk)
    except Exception:
        import logging
        logging.getLogger(__name__).warning(
            'Could not schedule checksum task for attachment %s — Celery may be unavailable.',
            attachment_pk,
        )


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
    FIX #7: max_length=200 prevents DoS via huge payloads holding DB connections.
    """
    fields = serializers.ListField(
        child=serializers.DictField(child=serializers.CharField(allow_blank=True)),
        allow_empty=True,
        max_length=200,   # FIX #7: hard cap — 200 custom fields per document is already extreme
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
    correspondent_name       = serializers.CharField(source='correspondent.name',       read_only=True)
    correspondent_short_code = serializers.CharField(source='correspondent.short_code', read_only=True)
    correspondent_org_type   = serializers.CharField(source='correspondent.org_type',   read_only=True)
    created_by_name          = serializers.SerializerMethodField(read_only=True)

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
    resolution_note = serializers.CharField(required=False, allow_blank=True, default='')

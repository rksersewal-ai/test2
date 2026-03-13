# =============================================================================
# FILE: apps/edms/serializers.py
# FIX (#2): FileAttachmentSerializer now validates file on upload
#           and auto-computes SHA-256 checksum.
# FIX (#5): Revision prepared_by / approved_by changed to FK reference.
# =============================================================================
from rest_framework import serializers
from apps.edms.models import Document, Revision, FileAttachment, Category, DocumentType
from apps.edms.validators import validate_document_file, compute_sha256


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'code', 'name', 'description', 'parent', 'is_active']


class DocumentTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = DocumentType
        fields = ['id', 'code', 'name', 'description', 'is_active']


class DocumentListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
        fields = [
            'id', 'document_number', 'title', 'status',
            'category', 'document_type', 'section',
            'source_standard', 'eoffice_file_number',
            'created_at', 'updated_at',
        ]


class DocumentDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
        fields = '__all__'
        read_only_fields = ['created_by', 'created_at', 'updated_at']


class RevisionSerializer(serializers.ModelSerializer):
    """FIX (#5): prepared_by_id / approved_by_id are FK to core.User.
    The plain text fields prepared_by / approved_by are REMOVED.
    """
    prepared_by_name  = serializers.CharField(source='prepared_by.full_name',  read_only=True)
    approved_by_name  = serializers.CharField(source='approved_by.full_name',  read_only=True)

    class Meta:
        model  = Revision
        fields = [
            'id', 'document', 'revision_number', 'revision_date',
            'status', 'change_description',
            'prepared_by', 'prepared_by_name',
            'approved_by', 'approved_by_name',
            'eoffice_ref', 'created_by', 'created_at', 'updated_at',
        ]
        read_only_fields = ['created_by', 'created_at', 'updated_at',
                            'prepared_by_name', 'approved_by_name']


class FileAttachmentSerializer(serializers.ModelSerializer):
    """FIX (#2): validate file on upload; auto-compute SHA-256."""
    file_path = serializers.FileField(write_only=True)

    class Meta:
        model  = FileAttachment
        fields = [
            'id', 'revision', 'file_name', 'file_path',
            'file_size_bytes', 'file_type', 'page_count',
            'checksum_sha256', 'is_primary', 'uploaded_by', 'uploaded_at',
        ]
        read_only_fields = ['checksum_sha256', 'file_size_bytes',
                            'uploaded_by', 'uploaded_at']

    def validate_file_path(self, file):
        validate_document_file(file)  # raises ValidationError on violation
        return file

    def create(self, validated_data):
        file = validated_data['file_path']
        validated_data['file_name']        = file.name
        validated_data['file_size_bytes']  = file.size
        validated_data['checksum_sha256']  = compute_sha256(file)
        return super().create(validated_data)

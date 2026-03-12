"""EDMS serializers."""
from rest_framework import serializers
from apps.edms.models import Document, Revision, FileAttachment, Category, DocumentType


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'code', 'name', 'description', 'parent', 'is_active']


class DocumentTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = DocumentType
        fields = ['id', 'code', 'name', 'description', 'is_active']


class FileAttachmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = FileAttachment
        fields = [
            'id', 'revision', 'file_name', 'file_path', 'file_size_bytes',
            'file_type', 'page_count', 'checksum_sha256', 'is_primary',
            'uploaded_by', 'uploaded_at'
        ]
        read_only_fields = ['uploaded_at', 'checksum_sha256']


class RevisionSerializer(serializers.ModelSerializer):
    files = FileAttachmentSerializer(many=True, read_only=True)
    document_number = serializers.CharField(source='document.document_number', read_only=True)
    created_by_name = serializers.CharField(source='created_by.full_name', read_only=True)

    class Meta:
        model = Revision
        fields = [
            'id', 'document', 'document_number', 'revision_number', 'revision_date',
            'status', 'change_description', 'prepared_by', 'approved_by',
            'eoffice_ref', 'created_by', 'created_by_name', 'created_at', 'updated_at', 'files'
        ]
        read_only_fields = ['created_at', 'updated_at']


class DocumentListSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    section_name = serializers.CharField(source='section.name', read_only=True)
    revision_count = serializers.SerializerMethodField()

    class Meta:
        model = Document
        fields = [
            'id', 'document_number', 'title', 'category', 'category_name',
            'section', 'section_name', 'status', 'source_standard',
            'eoffice_file_number', 'revision_count', 'created_at', 'updated_at'
        ]

    def get_revision_count(self, obj):
        return obj.revisions.count()


class DocumentDetailSerializer(serializers.ModelSerializer):
    revisions = RevisionSerializer(many=True, read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)
    section_name = serializers.CharField(source='section.name', read_only=True)
    created_by_name = serializers.CharField(source='created_by.full_name', read_only=True)

    class Meta:
        model = Document
        fields = [
            'id', 'document_number', 'title', 'description', 'category', 'category_name',
            'document_type', 'section', 'section_name', 'status', 'source_standard',
            'eoffice_file_number', 'eoffice_subject', 'keywords',
            'created_by', 'created_by_name', 'created_at', 'updated_at', 'revisions'
        ]
        read_only_fields = ['created_at', 'updated_at']

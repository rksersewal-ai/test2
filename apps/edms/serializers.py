"""EDMS serializers — complete replacement, aligned with models and frontend types."""
from rest_framework import serializers
from apps.edms.models import Document, Revision, FileAttachment, Category, DocumentType


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'code', 'description', 'is_active']


class DocumentTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = DocumentType
        fields = ['id', 'name', 'code', 'description', 'is_active']


class FileAttachmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = FileAttachment
        fields = [
            'id', 'file_name', 'file_size', 'content_type',
            'ocr_status', 'uploaded_at',
        ]
        read_only_fields = ['uploaded_at', 'ocr_status']


class RevisionSerializer(serializers.ModelSerializer):
    files = FileAttachmentSerializer(many=True, read_only=True)
    created_by_name = serializers.SerializerMethodField()

    class Meta:
        model = Revision
        fields = [
            'id', 'document', 'revision_number', 'revision_date', 'status',
            'change_description', 'eoffice_ref', 'created_by', 'created_by_name',
            'created_at', 'files',
        ]
        read_only_fields = ['created_at', 'created_by']

    def get_created_by_name(self, obj):
        return obj.created_by.get_full_name() if obj.created_by else None


class DocumentListSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True, default=None)
    section_name = serializers.CharField(source='section.name', read_only=True, default=None)
    document_type_name = serializers.CharField(source='document_type.name', read_only=True, default=None)
    revision_count = serializers.IntegerField(read_only=True, default=0)

    class Meta:
        model = Document
        fields = [
            'id', 'document_number', 'title', 'status',
            'category', 'category_name',
            'section', 'section_name',
            'document_type', 'document_type_name',
            'source_standard', 'revision_count',
            'created_at', 'updated_at',
        ]


class DocumentDetailSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True, default=None)
    section_name = serializers.CharField(source='section.name', read_only=True, default=None)
    document_type_name = serializers.CharField(source='document_type.name', read_only=True, default=None)
    created_by_name = serializers.SerializerMethodField()
    revisions = RevisionSerializer(many=True, read_only=True)

    class Meta:
        model = Document
        fields = [
            'id', 'document_number', 'title', 'description', 'status',
            'category', 'category_name',
            'section', 'section_name',
            'document_type', 'document_type_name',
            'source_standard', 'keywords',
            'eoffice_file_number', 'eoffice_subject',
            'created_by', 'created_by_name',
            'created_at', 'updated_at',
            'revisions',
        ]
        read_only_fields = ['created_at', 'updated_at', 'created_by']

    def get_created_by_name(self, obj):
        return obj.created_by.get_full_name() if obj.created_by else None

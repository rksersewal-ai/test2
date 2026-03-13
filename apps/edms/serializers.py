# =============================================================================
# FILE: apps/edms/serializers.py
# FIX (#2): FileAttachmentSerializer now validates size, MIME, and magic bytes.
# FIX (#5): Revision.prepared_by / approved_by validated as user references.
# =============================================================================
from rest_framework import serializers
from apps.edms.models import Document, Revision, FileAttachment, Category, DocumentType
from apps.edms.validators import validate_file_upload
from django.contrib.auth import get_user_model

User = get_user_model()


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'code', 'name', 'description', 'parent', 'is_active']


class DocumentTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = DocumentType
        fields = ['id', 'code', 'name', 'description', 'is_active']


class DocumentListSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    document_type_name = serializers.CharField(source='document_type.name', read_only=True)
    section_name = serializers.CharField(source='section.name', read_only=True)

    class Meta:
        model = Document
        fields = [
            'id', 'document_number', 'title', 'status',
            'category_name', 'document_type_name', 'section_name',
            'source_standard', 'eoffice_file_number', 'created_at', 'updated_at',
        ]


class DocumentDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
        fields = '__all__'
        read_only_fields = ['created_by', 'created_at', 'updated_at']


class RevisionSerializer(serializers.ModelSerializer):
    # FIX (#5): prepared_by and approved_by are now validated user PKs.
    # Store as user FK — display names are read from User.full_name.
    prepared_by_name  = serializers.SerializerMethodField(read_only=True)
    approved_by_name  = serializers.SerializerMethodField(read_only=True)

    # Accept user PKs on write
    prepared_by_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.filter(is_active=True),
        source='prepared_by', write_only=True, required=False, allow_null=True
    )
    approved_by_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.filter(is_active=True),
        source='approved_by', write_only=True, required=False, allow_null=True
    )

    def get_prepared_by_name(self, obj):
        return obj.prepared_by.full_name if obj.prepared_by else ''

    def get_approved_by_name(self, obj):
        return obj.approved_by.full_name if obj.approved_by else ''

    class Meta:
        model = Revision
        fields = [
            'id', 'document', 'revision_number', 'revision_date', 'status',
            'change_description', 'prepared_by_id', 'prepared_by_name',
            'approved_by_id', 'approved_by_name',
            'eoffice_ref', 'created_by', 'created_at', 'updated_at',
        ]
        read_only_fields = ['created_by', 'created_at', 'updated_at']


class FileAttachmentSerializer(serializers.ModelSerializer):
    file = serializers.FileField(write_only=True)  # upload field

    class Meta:
        model = FileAttachment
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
        # FIX (#2): validate size, MIME, and magic bytes; return checksum
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

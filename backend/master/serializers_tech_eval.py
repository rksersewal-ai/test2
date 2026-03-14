# =============================================================================
# FILE: backend/master/serializers_tech_eval.py
# SERIALIZER: PLTechEvalDocumentSerializer
# =============================================================================
import os
from rest_framework import serializers
from django.conf import settings
from .models_tech_eval import PLTechEvalDocument


class PLTechEvalDocumentSerializer(serializers.ModelSerializer):
    uploaded_by  = serializers.SerializerMethodField()
    download_url = serializers.SerializerMethodField()

    class Meta:
        model  = PLTechEvalDocument
        fields = [
            'id', 'pl_number', 'tender_number', 'eval_year',
            'file_name', 'file_format', 'file_size_kb',
            'uploaded_by', 'uploaded_at', 'download_url',
        ]
        read_only_fields = [
            'id', 'file_name', 'file_format', 'file_size_kb',
            'uploaded_by', 'uploaded_at', 'download_url',
        ]

    def get_uploaded_by(self, obj):
        if obj.uploaded_by:
            return obj.uploaded_by.get_full_name() or obj.uploaded_by.username
        return 'System'

    def get_download_url(self, obj):
        request = self.context.get('request')
        if obj.document_file and request:
            return request.build_absolute_uri(obj.document_file.url)
        if obj.document_file:
            return f"{settings.MEDIA_URL}{obj.document_file.name}"
        return None


class PLTechEvalDocumentUploadSerializer(serializers.Serializer):
    """Write-side serializer used for uploads."""
    tender_number = serializers.CharField(max_length=100)
    eval_year     = serializers.IntegerField(min_value=2000, max_value=2099)
    file          = serializers.FileField()

    def validate_file(self, value):
        name = getattr(value, 'name', '') or ''
        ext  = name.rsplit('.', 1)[-1].lower() if '.' in name else ''
        if ext not in ('pdf', 'docx'):
            raise serializers.ValidationError(
                'Only PDF (.pdf) and DOCX (.docx) files are accepted.'
            )
        if value.size > 20 * 1024 * 1024:
            raise serializers.ValidationError('File size must be under 20 MB.')
        return value

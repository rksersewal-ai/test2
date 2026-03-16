# =============================================================================
# FILE: apps/versioning/serializers.py
# FR-006: REST serializers for DocumentVersion, VersionAnnotation, VersionDiff
# =============================================================================
from rest_framework import serializers
from .models import DocumentVersion, VersionAnnotation, VersionDiff


class DocumentVersionSerializer(serializers.ModelSerializer):
    created_by_username = serializers.CharField(
        source='created_by.username', read_only=True, default='unknown'
    )

    class Meta:
        model  = DocumentVersion
        fields = [
            'id', 'document', 'version_number', 'file_path', 'file_size_bytes',
            'checksum_sha256', 'status', 'edit_summary', 'is_major',
            'created_by', 'created_by_username', 'created_at', 'deleted_at',
        ]
        read_only_fields = ['id', 'version_number', 'checksum_sha256',
                            'created_at', 'created_by_username']


class VersionAnnotationSerializer(serializers.ModelSerializer):
    created_by_username = serializers.CharField(
        source='created_by.username', read_only=True
    )

    class Meta:
        model  = VersionAnnotation
        fields = ['id', 'version', 'text', 'created_by', 'created_by_username', 'created_at']
        read_only_fields = ['id', 'created_at', 'created_by_username']


class VersionDiffSerializer(serializers.ModelSerializer):
    class Meta:
        model  = VersionDiff
        fields = ['id', 'from_version', 'to_version', 'diff_content', 'diff_size', 'created_at']
        read_only_fields = ['id', 'diff_content', 'diff_size', 'created_at']

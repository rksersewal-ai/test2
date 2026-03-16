from rest_framework import serializers
from .models import DocumentVersion, AlterationHistory, VersionAnnotation, VersionDiff


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


class AlterationHistorySerializer(serializers.ModelSerializer):
    """PRD Table 13.9: alterationhistory serializer."""
    implemented_by_username = serializers.CharField(
        source='implemented_by.username', read_only=True, default=''
    )

    class Meta:
        model  = AlterationHistory
        fields = [
            'id', 'document', 'version', 'alteration_number', 'previous_alteration',
            'alteration_date', 'changes_description', 'change_reason', 'probable_impacts',
            'source_agency', 'source_reference', 'source_date',
            'affected_pl_numbers', 'implementation_status',
            'implemented_at_plw', 'implemented_by', 'implemented_by_username',
            'file_path_old', 'file_path_new', 'created_at',
        ]
        read_only_fields = ['id', 'created_at', 'implemented_by_username']


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

from rest_framework import serializers
from apps.audit.models import AuditLog, DocumentAccessLog


class AuditLogSerializer(serializers.ModelSerializer):
    user_full_name = serializers.CharField(source='user.full_name', read_only=True)

    class Meta:
        model = AuditLog
        fields = [
            'id', 'timestamp', 'user', 'username', 'user_full_name',
            'action', 'module', 'entity_type', 'entity_id', 'entity_identifier',
            'description', 'ip_address', 'user_agent', 'request_method', 'request_path',
            'before_value', 'after_value', 'changes', 'success', 'error_message', 'session_id'
        ]


class DocumentAccessLogSerializer(serializers.ModelSerializer):
    user_full_name = serializers.CharField(source='user.full_name', read_only=True)

    class Meta:
        model = DocumentAccessLog
        fields = [
            'id', 'timestamp', 'user', 'user_full_name', 'document_id',
            'revision_id', 'file_id', 'access_type', 'document_number',
            'ip_address', 'session_id'
        ]

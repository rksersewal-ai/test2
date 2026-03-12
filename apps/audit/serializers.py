from rest_framework import serializers
from apps.audit.models import AuditLog


class AuditLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = AuditLog
        fields = [
            'id', 'timestamp', 'username', 'user_full_name',
            'module', 'action',
            'entity_type', 'entity_id', 'entity_identifier',
            'description', 'extra_data',
            'ip_address', 'success',
        ]
        read_only_fields = fields

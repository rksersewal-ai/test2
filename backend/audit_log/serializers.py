from rest_framework import serializers
from .models import AuditLog


class AuditLogSerializer(serializers.ModelSerializer):
    user_name = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model  = AuditLog
        fields = [
            'id', 'user', 'user_name', 'action', 'model',
            'object_id', 'object_repr', 'changes',
            'description', 'ip_address', 'timestamp',
        ]
        read_only_fields = ['id', 'timestamp', 'user_name']

    def get_user_name(self, obj):
        if obj.user:
            return obj.user.get_full_name() or obj.user.username
        return 'System'

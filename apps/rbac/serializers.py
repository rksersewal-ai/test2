from rest_framework import serializers
from .models import UserRole, DocumentPermissionOverride


class UserRoleSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model  = UserRole
        fields = ['id', 'user', 'username', 'role', 'section', 'document_type',
                  'granted_by', 'granted_at', 'expires_at', 'is_active']
        read_only_fields = ['id', 'granted_at', 'username']


class DocumentPermissionOverrideSerializer(serializers.ModelSerializer):
    class Meta:
        model  = DocumentPermissionOverride
        fields = ['id', 'user', 'document', 'permission', 'override',
                  'reason', 'granted_by', 'created_at', 'expires_at']
        read_only_fields = ['id', 'created_at']

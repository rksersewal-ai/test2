# =============================================================================
# FILE: apps/workledger/dropdown_serializers.py
# PURPOSE: Serializers for dropdown CRUD and public list endpoints
# =============================================================================
from rest_framework import serializers
from .dropdown_models import DropdownMaster, DropdownAuditLog


class DropdownItemSerializer(serializers.ModelSerializer):
    """Public read serializer - returns code, label, sort info."""
    class Meta:
        model  = DropdownMaster
        fields = ['id', 'code', 'label', 'sort_override', 'is_system']


class DropdownGroupSerializer(serializers.Serializer):
    """Response shape for a full dropdown group."""
    group_key = serializers.CharField()
    label     = serializers.CharField()
    items     = DropdownItemSerializer(many=True)


class DropdownCreateSerializer(serializers.ModelSerializer):
    """Admin: create a new dropdown item."""
    class Meta:
        model  = DropdownMaster
        fields = ['group_key', 'code', 'label', 'sort_override']

    def validate_code(self, value):
        # Codes must be safe machine identifiers
        import re
        if not re.match(r'^[A-Z0-9_]{1,80}$', value.upper()):
            raise serializers.ValidationError(
                'Code must contain only letters, digits, and underscores.'
            )
        return value.upper()

    def validate(self, data):
        group_key = data.get('group_key')
        code      = data.get('code')
        if DropdownMaster.objects.filter(group_key=group_key, code=code).exists():
            raise serializers.ValidationError(
                {'code': f'Code "{code}" already exists in group "{group_key}".'}
            )
        return data


class DropdownUpdateSerializer(serializers.ModelSerializer):
    """Admin: update label and/or sort_override.
    Code and group_key are immutable after creation.
    System items (is_system=True) only allow label/sort_override changes.
    """
    class Meta:
        model  = DropdownMaster
        fields = ['label', 'sort_override', 'is_active']

    def validate(self, data):
        instance = self.instance
        # System items must stay active (cannot be deactivated via API)
        if instance and instance.is_system and data.get('is_active') is False:
            raise serializers.ValidationError(
                {'is_active': 'System dropdown items cannot be deactivated.'}
            )
        return data


class DropdownAuditLogSerializer(serializers.ModelSerializer):
    class Meta:
        model  = DropdownAuditLog
        fields = ['log_id', 'group_key', 'code', 'action', 'old_label',
                  'new_label', 'changed_by', 'changed_at']

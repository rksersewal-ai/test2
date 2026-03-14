# =============================================================================
# FILE: apps/dashboard/serializers.py
# SPRINT 2 | FEATURE #7: Saved Views serializers
# =============================================================================
from rest_framework import serializers
from apps.dashboard.models import UserSavedView


class UserSavedViewSerializer(serializers.ModelSerializer):
    """
    Serializes a saved view for read and write.
    user is always set from request.user (write_only=True prevents client override).
    """
    user_display = serializers.SerializerMethodField(read_only=True)

    def get_user_display(self, obj):
        return obj.user.get_full_name() or obj.user.username

    class Meta:
        model  = UserSavedView
        fields = [
            'id', 'user', 'user_display',
            'view_name', 'module',
            'filter_json', 'widget_config_json',
            'is_pinned', 'sort_order', 'icon',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['user', 'created_at', 'updated_at']


class ReorderSavedViewsSerializer(serializers.Serializer):
    """
    Accepts a list of {id, sort_order} pairs for bulk reorder.
    POST /api/dashboard/saved-views/reorder/
    """
    items = serializers.ListField(
        child=serializers.DictField(child=serializers.IntegerField())
    )

    def validate_items(self, value):
        for item in value:
            if 'id' not in item or 'sort_order' not in item:
                raise serializers.ValidationError(
                    'Each item must have id and sort_order.'
                )
        return value

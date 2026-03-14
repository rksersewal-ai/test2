# =============================================================================
# FILE: apps/notifications/serializers.py
# SPRINT 4 — Notification serializers
# =============================================================================
from rest_framework import serializers
from apps.notifications.models import Notification


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Notification
        fields = [
            'id', 'kind', 'title', 'body', 'action_url',
            'is_read', 'created_at', 'expires_at',
        ]
        read_only_fields = ['kind', 'title', 'body', 'action_url',
                            'created_at', 'expires_at']

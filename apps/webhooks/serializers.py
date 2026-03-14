# =============================================================================
# FILE: apps/webhooks/serializers.py
# SPRINT 7
# =============================================================================
from rest_framework import serializers
from apps.webhooks.models import WebhookEndpoint, WebhookDelivery


class WebhookEndpointSerializer(serializers.ModelSerializer):
    created_by_name  = serializers.CharField(
        source='created_by.get_full_name', read_only=True
    )
    # Never expose secret in list/detail — write-only
    secret = serializers.CharField(write_only=True, required=False)

    class Meta:
        model  = WebhookEndpoint
        fields = [
            'id', 'name', 'url', 'secret', 'events',
            'is_active', 'timeout_seconds', 'max_retries',
            'created_by', 'created_by_name', 'created_at', 'updated_at',
        ]
        read_only_fields = ['created_by', 'created_at', 'updated_at']


class WebhookDeliverySerializer(serializers.ModelSerializer):
    endpoint_name = serializers.CharField(source='endpoint.name', read_only=True)

    class Meta:
        model  = WebhookDelivery
        fields = [
            'id', 'endpoint', 'endpoint_name', 'event_name',
            'status', 'attempt_count',
            'response_status', 'response_body', 'error_message',
            'next_retry_at', 'delivered_at', 'created_at',
        ]
        read_only_fields = fields

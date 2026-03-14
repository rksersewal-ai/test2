# =============================================================================
# FILE: apps/webhooks/models.py
# SPRINT 7 — Webhook endpoint registry + delivery log
#
# Event model:
#   Publisher (edms/workflow/etc.) calls:
#     from apps.webhooks.bus import emit
#     emit('document.created', payload={'document_id': doc.pk, ...})
#
#   The bus finds all active WebhookEndpoints subscribed to that event
#   and enqueues a WebhookDelivery via Celery.
#
# Security: every outgoing request carries
#   X-EDMS-Signature: sha256=<HMAC-SHA256(secret, body)>
#   X-EDMS-Event: <event_name>
#   X-EDMS-Delivery: <delivery_id>
#
# Retry strategy: exponential back-off, max 5 attempts.
# =============================================================================
import secrets
from django.db import models
from django.conf import settings


def _default_secret():
    return secrets.token_hex(32)   # 64-char hex string


class WebhookEndpoint(models.Model):
    """One registered HTTP endpoint that wants to receive EDMS events."""

    BUILTIN_EVENTS = [
        'document.created',
        'document.status_changed',
        'revision.created',
        'file.uploaded',
        'approval.submitted',
        'approval.approved',
        'approval.rejected',
        'share_link.created',
        'share_link.revoked',
        'sanity.errors_found',
    ]

    name            = models.CharField(max_length=200)
    url             = models.URLField(max_length=500)
    secret          = models.CharField(
        max_length=128, default=_default_secret,
        help_text='Used to compute HMAC-SHA256 signature on every delivery.'
    )
    # Subscribed events: JSON list of event names, e.g. ["document.created"]
    # Empty list = subscribe to ALL events.
    events          = models.JSONField(
        default=list,
        help_text='List of event names to deliver. Empty = all events.'
    )
    is_active       = models.BooleanField(default=True)
    timeout_seconds = models.IntegerField(default=10)
    max_retries     = models.IntegerField(default=5)
    created_by      = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='webhook_endpoints'
    )
    created_at      = models.DateTimeField(auto_now_add=True)
    updated_at      = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'webhook_endpoint'
        ordering = ['name']

    def __str__(self):
        return f'{self.name} → {self.url}'

    def subscribes_to(self, event_name: str) -> bool:
        """True if this endpoint should receive the given event."""
        return not self.events or event_name in self.events


class WebhookDelivery(models.Model):
    """Immutable delivery attempt record for one event to one endpoint."""

    class DeliveryStatus(models.TextChoices):
        PENDING   = 'PENDING',   'Pending'
        SUCCESS   = 'SUCCESS',   'Success'
        FAILED    = 'FAILED',    'Failed'
        RETRYING  = 'RETRYING',  'Retrying'
        ABANDONED = 'ABANDONED', 'Abandoned (max retries)'

    endpoint        = models.ForeignKey(
        WebhookEndpoint, on_delete=models.CASCADE, related_name='deliveries'
    )
    event_name      = models.CharField(max_length=100, db_index=True)
    payload         = models.JSONField(default=dict)
    status          = models.CharField(
        max_length=10, choices=DeliveryStatus.choices,
        default=DeliveryStatus.PENDING
    )
    attempt_count   = models.IntegerField(default=0)
    response_status = models.IntegerField(
        null=True, blank=True,
        help_text='HTTP status code of last delivery attempt'
    )
    response_body   = models.TextField(blank=True)
    error_message   = models.TextField(blank=True)
    next_retry_at   = models.DateTimeField(null=True, blank=True)
    delivered_at    = models.DateTimeField(null=True, blank=True)
    created_at      = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'webhook_delivery'
        ordering = ['-created_at']
        indexes  = [
            models.Index(fields=['status', 'next_retry_at']),
            models.Index(fields=['endpoint', 'event_name']),
        ]

    def __str__(self):
        return f'Delivery #{self.pk} [{self.event_name}] → {self.endpoint.name} [{self.status}]'

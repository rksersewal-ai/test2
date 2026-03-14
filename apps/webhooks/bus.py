# =============================================================================
# FILE: apps/webhooks/bus.py
# SPRINT 7 — Event bus
#
# Single public function: emit(event_name, payload)
#
# Callers across the codebase:
#   from apps.webhooks.bus import emit
#   emit('document.created', {'document_id': doc.pk, 'document_number': doc.document_number})
#
# The bus is intentionally fire-and-forget from the caller's perspective.
# All delivery happens asynchronously via Celery tasks.
# =============================================================================
import logging

log = logging.getLogger('webhooks')


def emit(event_name: str, payload: dict):
    """
    Broadcast an event to all subscribed active WebhookEndpoints.
    Enqueues one Celery task per endpoint.
    Safe to call inside Django ORM transactions — tasks are only
    dispatched after the current DB transaction commits.
    """
    try:
        from django.db import transaction
        from apps.webhooks.models import WebhookEndpoint, WebhookDelivery
        from apps.webhooks.tasks  import deliver_webhook

        def _dispatch():
            endpoints = WebhookEndpoint.objects.filter(is_active=True)
            for ep in endpoints:
                if not ep.subscribes_to(event_name):
                    continue
                delivery = WebhookDelivery.objects.create(
                    endpoint   = ep,
                    event_name = event_name,
                    payload    = payload,
                )
                deliver_webhook.delay(delivery.pk)
                log.debug(f'[Bus] Queued delivery #{delivery.pk} [{event_name}] → {ep.name}')

        # Execute after current transaction commits (avoids FK read before write)
        transaction.on_commit(_dispatch)

    except Exception as e:
        # Never let the event bus crash the calling code path
        log.error(f'[Bus] emit failed for {event_name}: {e}')

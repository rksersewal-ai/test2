# =============================================================================
# FILE: apps/webhooks/tasks.py
# SPRINT 7 — Webhook delivery Celery task
#
# Retry strategy: exponential back-off
#   Attempt 1 → immediate
#   Attempt 2 → 60 s
#   Attempt 3 → 5 min
#   Attempt 4 → 30 min
#   Attempt 5 → 2 h
#   Attempt 6+ → ABANDONED
# =============================================================================
import hashlib
import hmac
import json
import logging
from datetime import timedelta

import requests
from celery      import shared_task
from django.utils import timezone

log = logging.getLogger('webhooks')

RETRY_DELAYS = [0, 60, 300, 1800, 7200]   # seconds per attempt index


def _sign(secret: str, body: bytes) -> str:
    """Compute HMAC-SHA256 signature for webhook body."""
    return 'sha256=' + hmac.new(
        secret.encode(), body, hashlib.sha256
    ).hexdigest()


@shared_task(name='webhooks.deliver', bind=True, max_retries=5)
def deliver_webhook(self, delivery_id: int):
    from apps.webhooks.models import WebhookDelivery

    try:
        delivery = WebhookDelivery.objects.select_related('endpoint').get(pk=delivery_id)
    except WebhookDelivery.DoesNotExist:
        log.error(f'[Webhook] Delivery #{delivery_id} not found')
        return

    ep = delivery.endpoint
    if not ep.is_active:
        delivery.status        = WebhookDelivery.DeliveryStatus.ABANDONED
        delivery.error_message = 'Endpoint deactivated before delivery.'
        delivery.save(update_fields=['status', 'error_message'])
        return

    delivery.attempt_count += 1
    delivery.status         = WebhookDelivery.DeliveryStatus.RETRYING
    delivery.save(update_fields=['attempt_count', 'status'])

    body = json.dumps({
        'event':       delivery.event_name,
        'delivery_id': delivery.pk,
        'payload':     delivery.payload,
        'sent_at':     timezone.now().isoformat(),
    }, ensure_ascii=False).encode()

    headers = {
        'Content-Type':       'application/json',
        'X-EDMS-Event':       delivery.event_name,
        'X-EDMS-Delivery':    str(delivery.pk),
        'X-EDMS-Signature':   _sign(ep.secret, body),
        'User-Agent':         'PLW-EDMS-Webhook/1.0',
    }

    try:
        resp = requests.post(
            ep.url, data=body, headers=headers,
            timeout=ep.timeout_seconds, verify=True
        )
        delivery.response_status = resp.status_code
        delivery.response_body   = resp.text[:2000]

        if 200 <= resp.status_code < 300:
            delivery.status       = WebhookDelivery.DeliveryStatus.SUCCESS
            delivery.delivered_at = timezone.now()
            delivery.save(update_fields=[
                'status', 'response_status', 'response_body',
                'delivered_at', 'attempt_count',
            ])
            log.info(
                f'[Webhook] Delivered #{delivery.pk} [{delivery.event_name}] '
                f'→ {ep.url} ({resp.status_code})'
            )
            return

        raise ValueError(f'Non-2xx status: {resp.status_code}')

    except Exception as exc:
        log.warning(
            f'[Webhook] Delivery #{delivery.pk} attempt {delivery.attempt_count} '
            f'failed: {exc}'
        )
        attempt = delivery.attempt_count
        if attempt <= len(RETRY_DELAYS):
            delay = RETRY_DELAYS[attempt - 1] if attempt - 1 < len(RETRY_DELAYS) else 7200
            delivery.next_retry_at = timezone.now() + timedelta(seconds=delay)
            delivery.status        = WebhookDelivery.DeliveryStatus.RETRYING
            delivery.error_message = str(exc)[:500]
            delivery.save(update_fields=[
                'status', 'error_message', 'next_retry_at',
                'response_status', 'response_body', 'attempt_count',
            ])
            raise self.retry(exc=exc, countdown=delay)
        else:
            delivery.status        = WebhookDelivery.DeliveryStatus.ABANDONED
            delivery.error_message = f'Max retries reached. Last error: {exc}'[:500]
            delivery.save(update_fields=[
                'status', 'error_message', 'attempt_count',
            ])

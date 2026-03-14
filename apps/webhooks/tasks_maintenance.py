# =============================================================================
# FILE: apps/webhooks/tasks_maintenance.py
# SPRINT 7 — Maintenance Celery task for webhook delivery log
# =============================================================================
from celery import shared_task
import logging

log = logging.getLogger('webhooks')


@shared_task(name='webhooks.purge_old_deliveries')
def purge_old_deliveries(days: int = 30):
    """
    Delete ABANDONED and SUCCESS delivery rows older than `days`.
    Keeps PENDING / RETRYING rows untouched.
    Runs weekly on Sundays at 02:00 IST.
    """
    from django.utils import timezone
    from datetime     import timedelta
    from apps.webhooks.models import WebhookDelivery

    cutoff = timezone.now() - timedelta(days=days)
    deleted, _ = WebhookDelivery.objects.filter(
        status__in = [
            WebhookDelivery.DeliveryStatus.ABANDONED,
            WebhookDelivery.DeliveryStatus.SUCCESS,
        ],
        created_at__lt = cutoff,
    ).delete()

    log.info(f'[Webhooks] Purged {deleted} old delivery records (>{days}d).')
    return {'deleted': deleted}

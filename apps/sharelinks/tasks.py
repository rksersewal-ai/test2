# =============================================================================
# FILE: apps/sharelinks/tasks.py
# SPRINT 7 — Celery maintenance tasks for share links
# =============================================================================
from celery import shared_task
import logging

log = logging.getLogger('sharelinks')


@shared_task(name='sharelinks.purge_expired')
def purge_expired_sharelinks():
    """
    Deactivate share links that have passed their expires_at.
    Runs daily at 00:30 IST.
    Does NOT delete rows — keeps audit history.
    """
    from django.utils import timezone
    from apps.sharelinks.models import ShareLink

    count = ShareLink.objects.filter(
        is_active=True, expires_at__lt=timezone.now()
    ).update(is_active=False)

    log.info(f'[ShareLinks] Deactivated {count} expired share links.')
    return {'deactivated': count}

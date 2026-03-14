# =============================================================================
# FILE: apps/sdr/tasks.py
#
# SDR module is now a simple issue register.
# No workflow = no escalation tasks needed.
#
# This file is intentionally minimal — kept for future reporting tasks only.
# =============================================================================
from celery import shared_task


@shared_task(name='sdr.placeholder')
def placeholder():
    """Reserved for future SDR reporting tasks."""
    return 'ok'

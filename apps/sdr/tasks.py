# =============================================================================
# FILE: apps/sdr/tasks.py
#
# Celery beat tasks for SDR module.
#
# SCHEDULED TASKS:
#   escalate_overdue_sdrs   — daily at 08:00 IST
#       Finds all SUBMITTED/ASSIGNED/IN_PROGRESS SDRs past target_response_date
#       and moves them to ESCALATED.
#       Sends an in-app notification to the assigned user and their supervisor.
#
#   send_sdr_daily_summary  — daily at 09:00 IST
#       Sends a summary count (open / overdue / production-hold) to all
#       Officer/WM-level users via the notifications app.
# =============================================================================
from celery import shared_task
from django.utils import timezone


@shared_task(bind=True, name='sdr.escalate_overdue_sdrs', max_retries=3)
def escalate_overdue_sdrs(self):
    """
    Auto-escalate SDRs that have passed their target_response_date.
    Runs daily at 08:00 IST via Celery beat.
    """
    from datetime import date
    from apps.sdr.models import SDRRequest

    today    = date.today()
    open_statuses = ['SUBMITTED', 'ASSIGNED', 'IN_PROGRESS']

    overdue = SDRRequest.objects.filter(
        status__in=open_statuses,
        target_response_date__lt=today,
    ).select_related('assigned_to', 'raised_by')

    escalated_ids = []
    for sdr in overdue:
        sdr.status = 'ESCALATED'
        sdr.save(update_fields=['status', 'updated_at'])
        escalated_ids.append(sdr.sdr_number)
        _notify_escalation(sdr)

    return {
        'date':      str(today),
        'escalated': len(escalated_ids),
        'sdr_numbers': escalated_ids,
    }


@shared_task(bind=True, name='sdr.send_daily_summary', max_retries=2)
def send_sdr_daily_summary(self):
    """
    Send a daily SDR status summary to Officer/WM-level users.
    """
    from apps.sdr.models import SDRRequest
    from datetime import date

    today         = date.today()
    open_count    = SDRRequest.objects.filter(
        status__in=['SUBMITTED', 'ASSIGNED', 'IN_PROGRESS', 'ESCALATED']
    ).count()
    overdue_count = SDRRequest.objects.filter(
        status__in=['SUBMITTED', 'ASSIGNED', 'IN_PROGRESS', 'ESCALATED'],
        target_response_date__lt=today,
    ).count()
    prod_hold_count = SDRRequest.objects.filter(
        status__in=['SUBMITTED', 'ASSIGNED', 'IN_PROGRESS', 'ESCALATED'],
        production_hold=True,
    ).count()
    escalated_count = SDRRequest.objects.filter(status='ESCALATED').count()

    message = (
        f'SDR Daily Summary ({today.strftime("%d-%b-%Y")}):\n'
        f'  Open       : {open_count}\n'
        f'  Overdue    : {overdue_count}\n'
        f'  Prod-Hold  : {prod_hold_count}\n'
        f'  Escalated  : {escalated_count}'
    )

    _notify_officers(message)
    return {'date': str(today), 'open': open_count, 'overdue': overdue_count}


# ---------------------------------------------------------------------------
def _notify_escalation(sdr):
    """Create an in-app notification for the assigned user and supervisor."""
    try:
        from apps.notifications.models import Notification
        recipients = []
        if sdr.assigned_to:
            recipients.append(sdr.assigned_to)
        if sdr.raised_by:
            recipients.append(sdr.raised_by)
        for user in recipients:
            Notification.objects.create(
                user    = user,
                title   = f'SDR Escalated: {sdr.sdr_number}',
                message = (
                    f'SDR {sdr.sdr_number} — "{sdr.subject[:80]}" '
                    f'has been auto-escalated as the target response date '
                    f'({sdr.target_response_date}) has passed.'
                ),
                category = 'SDR_ESCALATION',
                priority = 'HIGH' if sdr.production_hold else 'MEDIUM',
            )
    except Exception:
        pass  # Never let notification failure crash the task


def _notify_officers(message):
    """Send summary notification to all Officer/WM-level users."""
    try:
        from django.contrib.auth import get_user_model
        from apps.notifications.models import Notification
        User = get_user_model()
        officers = User.objects.filter(
            is_active=True,
            role__role_name__in=['Officer', 'WM', 'Admin'],
        )
        for user in officers:
            Notification.objects.create(
                user     = user,
                title    = 'SDR Daily Summary',
                message  = message,
                category = 'SDR_SUMMARY',
                priority = 'LOW',
            )
    except Exception:
        pass

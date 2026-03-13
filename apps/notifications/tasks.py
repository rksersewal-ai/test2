# =============================================================================
# FILE: apps/notifications/tasks.py
# SPRINT 4 — Celery tasks: scheduled cleanup + overdue work reminder
# Registered in celery_app.py beat schedule.
# =============================================================================
from celery import shared_task


@shared_task(name='notifications.purge_expired')
def purge_expired_notifications():
    """Delete expired notifications. Runs daily at 02:00."""
    from apps.notifications.services import NotificationService
    deleted = NotificationService.purge_expired()
    return {'deleted_expired': deleted}


@shared_task(name='notifications.purge_old_read')
def purge_old_read_notifications():
    """Delete read notifications older than 30 days. Runs weekly Sunday 03:00."""
    from apps.notifications.services import NotificationService
    deleted = NotificationService.purge_old_read(days=30)
    return {'deleted_old_read': deleted}


@shared_task(name='notifications.overdue_work_reminders')
def send_overdue_work_reminders():
    """
    Find WorkLedgerEntry rows past target_date with status OPEN or IN_PROGRESS.
    Notify the assigned_to user. Runs daily at 08:00.
    """
    from django.utils.timezone import now
    from apps.workflow.models import WorkLedgerEntry
    from apps.notifications.services import NotificationService

    today    = now().date()
    overdue  = WorkLedgerEntry.objects.filter(
        target_date__lt=today,
        status__in=['OPEN', 'IN_PROGRESS'],
        assigned_to__isnull=False,
    ).select_related('assigned_to')

    count = 0
    for entry in overdue:
        NotificationService.create(
            user       = entry.assigned_to,
            kind       = 'OVERDUE_WORK',
            title      = f'Overdue work: {entry.subject or entry.eoffice_subject or entry.pk}',
            body       = f'Target date was {entry.target_date}. Status: {entry.status}.',
            action_url = f'/work-ledger/?id={entry.pk}',
        )
        count += 1
    return {'overdue_reminders_sent': count}


@shared_task(name='notifications.approval_sla_reminders')
def send_approval_sla_reminders():
    """
    Find ApprovalRequests IN_REVIEW where the current step is past its SLA.
    Notify the assigned approver. Runs daily at 09:00.
    """
    from datetime import timedelta
    from django.utils.timezone import now
    from apps.workflow.models import ApprovalRequest, ApprovalStep
    from apps.notifications.services import NotificationService

    active = ApprovalRequest.objects.filter(
        status='IN_REVIEW'
    ).select_related('chain', 'revision__document')

    count = 0
    for req in active:
        step = ApprovalStep.objects.filter(
            chain=req.chain, step_order=req.current_step
        ).select_related('assigned_user').first()

        if not step or not step.assigned_user:
            continue

        sla_deadline = req.initiated_at + timedelta(days=step.due_days)
        if now() > sla_deadline:
            NotificationService.create(
                user       = step.assigned_user,
                kind       = 'WARNING',
                title      = f'Approval SLA overdue: {req.revision}',
                body       = (
                    f'Step "{step.label}" in chain "{req.chain.name}" '
                    f'was due by {sla_deadline.date()}. Please review.'
                ),
                action_url = f'/documents/{req.revision.document_id}/'
                             f'revisions/{req.revision_id}/approval/{req.pk}/',
            )
            count += 1
    return {'sla_reminders_sent': count}

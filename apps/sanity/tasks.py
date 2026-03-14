# =============================================================================
# FILE: apps/sanity/tasks.py
# SPRINT 6 — Celery task for scheduled sanity checks
# =============================================================================
from celery import shared_task
import logging

log = logging.getLogger('sanity')


@shared_task(name='sanity.run_checks')
def run_sanity_checks(stale_draft_days: int = 90, user_id: int = None):
    """
    Run all sanity checks, save a SanityReport, notify admin users of ERRORs.
    Runs automatically every Monday at 07:00 IST (01:30 UTC).
    Also callable on-demand from the admin UI.
    """
    from apps.sanity.checks  import run_all_checks
    from apps.sanity.models  import SanityReport

    user = None
    if user_id:
        from django.contrib.auth import get_user_model
        user = get_user_model().objects.filter(pk=user_id).first()

    issues = run_all_checks(stale_draft_days=stale_draft_days)

    errors   = [i for i in issues if i['severity'] == 'ERROR']
    warnings = [i for i in issues if i['severity'] == 'WARNING']
    infos    = [i for i in issues if i['severity'] == 'INFO']

    report = SanityReport.objects.create(
        run_by          = user,
        total_issues    = len(issues),
        error_count     = len(errors),
        warning_count   = len(warnings),
        info_count      = len(infos),
        issues          = issues,
        stale_draft_days = stale_draft_days,
    )

    # Notify admin users if any ERRORs found
    if errors:
        try:
            from django.contrib.auth import get_user_model
            from apps.notifications.services import NotificationService
            admins = get_user_model().objects.filter(is_staff=True)
            for admin_user in admins:
                NotificationService.create(
                    user       = admin_user,
                    kind       = 'ERROR',
                    title      = f'Sanity check: {len(errors)} ERROR(s) found',
                    body       = '; '.join(e['message'] for e in errors[:5]),
                    action_url = '/admin/sanity/',
                )
        except Exception as e:
            log.warning(f'[Sanity] Notification failed: {e}')

    log.info(
        f'[Sanity] Report #{report.pk}: '
        f'{len(errors)}E {len(warnings)}W {len(infos)}I'
    )
    return {
        'report_id':   report.pk,
        'errors':      len(errors),
        'warnings':    len(warnings),
        'info':        len(infos),
    }

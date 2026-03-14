# =============================================================================
# FILE: apps/sanity/models.py
# SPRINT 6 — SanityReport: stores each check run result
# =============================================================================
from django.db import models
from django.conf import settings


class SanityReport(models.Model):
    """Snapshot of one full sanity check run."""
    run_by          = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='sanity_reports'
    )
    ran_at          = models.DateTimeField(auto_now_add=True)
    total_issues    = models.IntegerField(default=0)
    error_count     = models.IntegerField(default=0)
    warning_count   = models.IntegerField(default=0)
    info_count      = models.IntegerField(default=0)
    # Full list of issue dicts (JSON)
    issues          = models.JSONField(default=list)
    stale_draft_days = models.IntegerField(default=90)

    class Meta:
        db_table = 'sanity_report'
        ordering = ['-ran_at']

    def __str__(self):
        return (
            f'SanityReport #{self.pk} '
            f'[{self.error_count}E {self.warning_count}W {self.info_count}I] '
            f'{self.ran_at.strftime("%Y-%m-%d %H:%M")}'
        )

# =============================================================================
# FILE: apps/dashboard/models.py
# SPRINT 2 | FEATURE #7: Customisable Saved Views / Dashboard Widgets
# PURPOSE : Per-user saved filter presets and optional dashboard widget config.
#           Pinned views appear in the sidebar. filter_json stores the exact
#           query-string parameters so the frontend can replay the list view.
# =============================================================================
from django.db import models
from django.conf import settings


class UserSavedView(models.Model):
    """
    A saved filter preset for EDMS list, WorkLedger list, or Dashboard.

    filter_json examples:
      EDMS      : {"status": "ACTIVE", "category": 3, "section": 7, "q": "WAG9"}
      WORKLEDGER: {"status": "OPEN", "work_type": 2}
      DASHBOARD : {"chart_type": "bar", "metric": "documents_by_section", "limit": 10}
    """
    class Module(models.TextChoices):
        EDMS       = 'EDMS',       'EDMS Documents'
        WORKLEDGER = 'WORKLEDGER', 'Work Ledger'
        DASHBOARD  = 'DASHBOARD',  'Dashboard Widget'

    user               = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='saved_views'
    )
    view_name          = models.CharField(max_length=120)
    module             = models.CharField(max_length=20, choices=Module.choices,
                                          default=Module.EDMS)
    filter_json        = models.JSONField(default=dict, blank=True)
    widget_config_json = models.JSONField(default=dict, blank=True,
                                          help_text='Optional dashboard widget display config.')
    is_pinned          = models.BooleanField(default=False,
                                             help_text='Pinned views appear in sidebar.')
    sort_order         = models.IntegerField(default=0)
    icon               = models.CharField(max_length=40, blank=True,
                                          help_text='Icon key for sidebar e.g. filter, star, folder')
    created_at         = models.DateTimeField(auto_now_add=True)
    updated_at         = models.DateTimeField(auto_now=True)

    class Meta:
        db_table        = 'user_saved_view'
        unique_together = [('user', 'view_name', 'module')]
        ordering        = ['module', 'sort_order', 'view_name']

    def __str__(self):
        pinned = ' 📌' if self.is_pinned else ''
        return f"{self.user.get_full_name()} / [{self.module}] {self.view_name}{pinned}"

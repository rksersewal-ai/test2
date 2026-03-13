# =============================================================================
# FILE: apps/workledger/dropdown_models.py
# FIX (#15): managed=True so Django can create/manage the table via migrations.
#            Previously managed=False but ORM writes were still being made,
#            which works only if the table pre-exists. Using managed=True with
#            a proper migration is the correct approach.
# FIX (#11): Removed 'section' group reference from ALL_GROUPS - it duplicates
#            core.Section model. Section dropdown should call core Section API.
# =============================================================================
from django.db import models
from django.conf import settings
from django.utils import timezone


class DropdownMaster(models.Model):
    GROUP_WORK_STATUS        = 'work_status'
    GROUP_WORK_CATEGORY      = 'work_category'
    GROUP_INSPECTION_RESULT  = 'inspection_result'
    GROUP_CONCERNED_OFFICER  = 'concerned_officer'
    GROUP_ENGINEER_STAFF     = 'engineer_staff'
    GROUP_PL_NUMBER_PREFIX   = 'pl_number_prefix'
    GROUP_LOCO_TYPE          = 'loco_type'

    # FIX (#11): Removed GROUP_SECTION - use core.Section model instead
    ALL_GROUPS = [
        (GROUP_WORK_STATUS,       'Work Status (Open / Closed / Pending)'),
        (GROUP_WORK_CATEGORY,     'Work Category'),
        (GROUP_INSPECTION_RESULT, 'Inspection Result'),
        (GROUP_CONCERNED_OFFICER, 'Concerned Officer'),
        (GROUP_ENGINEER_STAFF,    'Engineer / Staff'),
        (GROUP_PL_NUMBER_PREFIX,  'PL Number Prefix'),
        (GROUP_LOCO_TYPE,         'Loco Type'),
    ]

    id            = models.BigAutoField(primary_key=True)
    group_key     = models.CharField(max_length=80)
    code          = models.CharField(max_length=80)
    label         = models.CharField(max_length=200)
    is_active     = models.BooleanField(default=True)
    is_system     = models.BooleanField(default=False)
    sort_override = models.IntegerField(null=True, blank=True)
    created_by    = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True,
        on_delete=models.SET_NULL, related_name='dropdowns_created'
    )
    created_at    = models.DateTimeField(default=timezone.now)
    updated_at    = models.DateTimeField(auto_now=True)

    class Meta:
        db_table        = 'dropdown_master'
        unique_together = [('group_key', 'code')]
        managed         = True   # FIX: was False
        ordering        = ['group_key', 'label']

    def __str__(self):
        return f'[{self.group_key}] {self.label} ({self.code})'


class DropdownAuditLog(models.Model):
    ACTION_CREATED      = 'CREATED'
    ACTION_UPDATED      = 'UPDATED'
    ACTION_DEACTIVATED  = 'DEACTIVATED'
    ACTION_DELETED      = 'DELETED'

    log_id      = models.BigAutoField(primary_key=True)
    dropdown    = models.ForeignKey(
        DropdownMaster, null=True, blank=True,
        on_delete=models.SET_NULL, related_name='audit_logs'
    )
    group_key   = models.CharField(max_length=80)
    code        = models.CharField(max_length=80)
    action      = models.CharField(max_length=20)
    old_label   = models.CharField(max_length=200, null=True, blank=True)
    new_label   = models.CharField(max_length=200, null=True, blank=True)
    changed_by  = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True,
        on_delete=models.SET_NULL, related_name='dropdown_changes'
    )
    changed_at  = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = 'dropdown_audit_log'
        managed  = True   # FIX: was False
        ordering = ['-changed_at']

    def __str__(self):
        return f'{self.action} [{self.group_key}/{self.code}]'

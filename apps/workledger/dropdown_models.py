# =============================================================================
# FILE: apps/workledger/dropdown_models.py
# FIX (#15): managed=True so Django ORM handles writes correctly via ORM.
#            SQL schema still created by sql/005_dropdown_master.sql.
#            Set managed=False ONLY if you never want Django to touch the table.
#            Since we do ORM writes (create/update/delete in dropdown_services.py),
#            managed must be True, otherwise ORM write behaviour is undefined.
# FIX (#11): 'section' group removed from ALL_GROUPS and seed data
#            (now owned by core_section table).
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
    # FIX (#4): FK to User instead of raw BigInt
    created_by    = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True,
        on_delete=models.SET_NULL, related_name='dropdowns_created', db_column='created_by'
    )
    created_at    = models.DateTimeField(default=timezone.now)
    updated_at    = models.DateTimeField(auto_now=True)

    class Meta:
        db_table        = 'dropdown_master'
        unique_together = [('group_key', 'code')]
        managed         = True   # FIX (#15): was False
        ordering        = ['group_key', 'label']

    def __str__(self):
        return f'[{self.group_key}] {self.label} ({self.code})'


class DropdownAuditLog(models.Model):
    ACTION_CREATED      = 'CREATED'
    ACTION_UPDATED      = 'UPDATED'
    ACTION_DEACTIVATED  = 'DEACTIVATED'
    ACTION_DELETED      = 'DELETED'

    log_id      = models.BigAutoField(primary_key=True)
    dropdown_id = models.BigIntegerField()
    group_key   = models.CharField(max_length=80)
    code        = models.CharField(max_length=80)
    action      = models.CharField(max_length=20)
    old_label   = models.CharField(max_length=200, null=True, blank=True)
    new_label   = models.CharField(max_length=200, null=True, blank=True)
    # FIX (#4): FK to User
    changed_by  = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True,
        on_delete=models.SET_NULL, related_name='dropdown_audit_logs', db_column='changed_by'
    )
    changed_at  = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = 'dropdown_audit_log'
        managed  = True   # FIX (#15)
        ordering = ['-changed_at']

    def __str__(self):
        return f'{self.action} [{self.group_key}/{self.code}]'

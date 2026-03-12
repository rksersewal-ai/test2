"""LDO Work Ledger models.

Philosophy: factual record-keeping only.
No approval engine, no workflow automation.
All status transitions are manual and recorded via audit log.
"""
from django.db import models
from django.conf import settings


class WorkType(models.Model):
    """Master list of work categories used in LDO."""
    name = models.CharField(max_length=120, unique=True)
    code = models.CharField(max_length=20, unique=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'workflow_work_type'
        ordering = ['name']

    def __str__(self):
        return self.name


class WorkLedgerEntry(models.Model):
    """Single unit of recorded work in the LDO work ledger."""

    class Status(models.TextChoices):
        OPEN = 'OPEN', 'Open'
        IN_PROGRESS = 'IN_PROGRESS', 'In Progress'
        ON_HOLD = 'ON_HOLD', 'On Hold'
        CLOSED = 'CLOSED', 'Closed'

    work_type = models.ForeignKey(
        WorkType, on_delete=models.PROTECT,
        related_name='entries', null=True, blank=True,
    )
    subject = models.CharField(max_length=500, blank=True)
    description = models.TextField(blank=True)

    # eOffice cross-reference (read-only link, not approval engine)
    eoffice_file_number = models.CharField(max_length=100, blank=True, db_index=True)
    eoffice_subject = models.CharField(max_length=500, blank=True)
    eoffice_diary_number = models.CharField(max_length=100, blank=True)

    # Organisational
    section = models.ForeignKey(
        'core.Section', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='work_entries',
    )
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='assigned_work_entries',
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='created_work_entries',
    )

    # Document/Revision linkage
    linked_document = models.ForeignKey(
        'edms.Document', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='work_entries',
    )
    linked_revision = models.ForeignKey(
        'edms.Revision', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='work_entries',
    )

    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.OPEN, db_index=True,
    )
    received_date = models.DateField(null=True, blank=True)
    target_date = models.DateField(null=True, blank=True)
    closed_date = models.DateField(null=True, blank=True)

    remarks = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'workflow_work_ledger_entry'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['section']),
            models.Index(fields=['assigned_to']),
            models.Index(fields=['eoffice_file_number']),
            models.Index(fields=['target_date']),
        ]

    def __str__(self):
        return f'[{self.status}] {self.subject or self.eoffice_subject or self.pk}'

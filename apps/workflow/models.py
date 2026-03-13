# =============================================================================
# FILE: apps/workflow/models.py
# SPRINT 4: Added ApprovalChain, ApprovalStep, ApprovalRequest, ApprovalVote
# All Sprint 1 models (WorkType, WorkLedgerEntry) preserved exactly.
# =============================================================================
"""LDO Work Ledger + Document Approval Workflow models."""
from django.db import models
from django.conf import settings


# ---------------------------------------------------------------------------
# Existing (Sprint 0/1) — preserved exactly
# ---------------------------------------------------------------------------

class WorkType(models.Model):
    name        = models.CharField(max_length=120, unique=True)
    code        = models.CharField(max_length=20,  unique=True)
    description = models.TextField(blank=True)
    is_active   = models.BooleanField(default=True)

    class Meta:
        db_table = 'workflow_work_type'
        ordering = ['name']

    def __str__(self):
        return self.name


class WorkLedgerEntry(models.Model):
    class Status(models.TextChoices):
        OPEN        = 'OPEN',        'Open'
        IN_PROGRESS = 'IN_PROGRESS', 'In Progress'
        ON_HOLD     = 'ON_HOLD',     'On Hold'
        CLOSED      = 'CLOSED',      'Closed'

    work_type            = models.ForeignKey(WorkType, on_delete=models.PROTECT,
                               related_name='entries', null=True, blank=True)
    subject              = models.CharField(max_length=500, blank=True)
    description          = models.TextField(blank=True)
    eoffice_file_number  = models.CharField(max_length=100, blank=True, db_index=True)
    eoffice_subject      = models.CharField(max_length=500, blank=True)
    eoffice_diary_number = models.CharField(max_length=100, blank=True)
    section              = models.ForeignKey('core.Section', on_delete=models.SET_NULL,
                               null=True, blank=True, related_name='work_entries')
    assigned_to          = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
                               null=True, blank=True, related_name='assigned_work_entries')
    created_by           = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
                               null=True, blank=True, related_name='created_work_entries')
    linked_document      = models.ForeignKey('edms.Document', on_delete=models.SET_NULL,
                               null=True, blank=True, related_name='work_entries')
    linked_revision      = models.ForeignKey('edms.Revision', on_delete=models.SET_NULL,
                               null=True, blank=True, related_name='work_entries')
    status               = models.CharField(max_length=20, choices=Status.choices,
                               default=Status.OPEN, db_index=True)
    received_date        = models.DateField(null=True, blank=True)
    target_date          = models.DateField(null=True, blank=True)
    closed_date          = models.DateField(null=True, blank=True)
    remarks              = models.TextField(blank=True)
    created_at           = models.DateTimeField(auto_now_add=True)
    updated_at           = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'workflow_work_ledger_entry'
        ordering = ['-created_at']
        indexes  = [
            models.Index(fields=['status']),
            models.Index(fields=['section']),
            models.Index(fields=['assigned_to']),
            models.Index(fields=['eoffice_file_number']),
            models.Index(fields=['target_date']),
        ]

    def __str__(self):
        return f'[{self.status}] {self.subject or self.eoffice_subject or self.pk}'


# ---------------------------------------------------------------------------
# Sprint 4 — Approval Engine
# ---------------------------------------------------------------------------

class ApprovalChain(models.Model):
    """
    A named, reusable approval workflow template.
    Can be tied to a specific DocumentType or left universal (document_type=None).
    """
    name          = models.CharField(max_length=200)
    document_type = models.ForeignKey(
        'edms.DocumentType', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='approval_chains',
        help_text='Leave blank for a universal chain applicable to any document type.'
    )
    is_active     = models.BooleanField(default=True)
    created_by    = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='created_approval_chains'
    )
    created_at    = models.DateTimeField(auto_now_add=True)
    updated_at    = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'workflow_approval_chain'
        ordering = ['name']

    def __str__(self):
        scope = self.document_type.name if self.document_type_id else 'Universal'
        return f'{self.name} ({scope})'


class ApprovalStep(models.Model):
    """
    One ordered approver slot within an ApprovalChain.
    Either role or assigned_user must be set; both may be set (role filters
    the candidates, assigned_user is the default selection).
    """
    chain         = models.ForeignKey(ApprovalChain, on_delete=models.CASCADE,
                        related_name='steps')
    step_order    = models.IntegerField(default=0)
    label         = models.CharField(max_length=120,
                        help_text='e.g. Checker, Section Engineer, HOD')
    role          = models.CharField(max_length=50, blank=True)
    assigned_user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='approval_steps'
    )
    due_days      = models.IntegerField(default=3,
                        help_text='SLA: days from step activation to expected vote')
    is_optional   = models.BooleanField(default=False)

    class Meta:
        db_table        = 'workflow_approval_step'
        ordering        = ['chain', 'step_order']
        unique_together = [('chain', 'step_order')]

    def __str__(self):
        return f'{self.chain.name} → Step {self.step_order}: {self.label}'


class ApprovalRequest(models.Model):
    """
    One execution of an ApprovalChain against a specific Revision.
    Tracks which step is currently active and the overall status.
    """
    class Status(models.TextChoices):
        PENDING    = 'PENDING',    'Pending'
        IN_REVIEW  = 'IN_REVIEW',  'In Review'
        APPROVED   = 'APPROVED',   'Approved'
        REJECTED   = 'REJECTED',   'Rejected'
        WITHDRAWN  = 'WITHDRAWN',  'Withdrawn'

    chain        = models.ForeignKey(ApprovalChain, on_delete=models.PROTECT,
                       related_name='requests')
    revision     = models.ForeignKey('edms.Revision', on_delete=models.CASCADE,
                       related_name='approval_requests')
    status       = models.CharField(max_length=20, choices=Status.choices,
                       default=Status.PENDING, db_index=True)
    current_step = models.IntegerField(default=0,
                       help_text='step_order of the currently active ApprovalStep')
    initiated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='initiated_approval_requests'
    )
    initiated_at  = models.DateTimeField(auto_now_add=True)
    completed_at  = models.DateTimeField(null=True, blank=True)
    remarks       = models.TextField(blank=True)

    class Meta:
        db_table        = 'workflow_approval_request'
        ordering        = ['-initiated_at']
        unique_together = [('revision', 'chain')]
        indexes         = [
            models.Index(fields=['status']),
            models.Index(fields=['revision']),
        ]

    def __str__(self):
        return f'ApprovalRequest #{self.pk} [{self.status}] — {self.revision}'


class ApprovalVote(models.Model):
    """
    One approver's decision on a single step of an ApprovalRequest.
    """
    class Vote(models.TextChoices):
        APPROVED   = 'APPROVED',   'Approved'
        REJECTED   = 'REJECTED',   'Rejected'
        DELEGATED  = 'DELEGATED',  'Delegated'
        RETURNED   = 'RETURNED',   'Returned for Correction'

    request  = models.ForeignKey(ApprovalRequest, on_delete=models.CASCADE,
                   related_name='votes')
    step     = models.ForeignKey(ApprovalStep, on_delete=models.PROTECT,
                   related_name='votes')
    voted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='approval_votes'
    )
    vote      = models.CharField(max_length=15, choices=Vote.choices)
    comment   = models.TextField(blank=True)
    voted_at  = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table        = 'workflow_approval_vote'
        unique_together = [('request', 'step')]
        indexes         = [
            models.Index(fields=['request']),
            models.Index(fields=['voted_by']),
        ]

    def __str__(self):
        return f'Vote [{self.vote}] by {self.voted_by} on {self.request}'

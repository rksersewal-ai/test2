# =============================================================================
# FILE: apps/lifecycle/models.py
# FR-011: Document Retention & Lifecycle Management
# Manages retention policies, scheduled archival, legal holds,
# permanent deletion (with audit trail), and lifecycle events.
# =============================================================================
from django.db import models
from django.conf import settings
from apps.edms.models import Document


class RetentionPolicy(models.Model):
    """Defines how long a document type must be retained before archival/deletion."""

    class ActionAfterRetention(models.TextChoices):
        ARCHIVE  = 'ARCHIVE',  'Move to Archive'
        DELETE   = 'DELETE',   'Permanent Delete'
        REVIEW   = 'REVIEW',   'Flag for Review'

    name                  = models.CharField(max_length=200, unique=True)
    description           = models.TextField(blank=True)
    retention_years       = models.PositiveIntegerField(
        help_text='Number of years to retain document'
    )
    action_after_retention = models.CharField(
        max_length=20, choices=ActionAfterRetention.choices,
        default=ActionAfterRetention.ARCHIVE
    )
    legal_basis           = models.CharField(
        max_length=300, blank=True,
        help_text='Legal or regulatory basis (e.g., Railways Act 1989, IT Act 2000)'
    )
    is_active             = models.BooleanField(default=True)
    created_by            = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True,
        on_delete=models.SET_NULL, related_name='retention_policies_created'
    )
    created_at            = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'lifecycle_retention_policy'
        ordering = ['retention_years', 'name']

    def __str__(self):
        return f"{self.name} ({self.retention_years} yrs → {self.action_after_retention})"


class DocumentLifecycle(models.Model):
    """Tracks the lifecycle state of a single document."""

    class LifecycleState(models.TextChoices):
        ACTIVE      = 'ACTIVE',      'Active'
        REVIEW_DUE  = 'REVIEW_DUE',  'Review Due'
        ARCHIVED    = 'ARCHIVED',    'Archived'
        LEGAL_HOLD  = 'LEGAL_HOLD',  'Legal Hold'
        PENDING_DEL = 'PENDING_DEL', 'Pending Deletion'
        DELETED     = 'DELETED',     'Permanently Deleted'

    document           = models.OneToOneField(
        Document, on_delete=models.CASCADE, related_name='lifecycle'
    )
    policy             = models.ForeignKey(
        RetentionPolicy, null=True, blank=True,
        on_delete=models.SET_NULL, related_name='document_lifecycles'
    )
    state              = models.CharField(
        max_length=20, choices=LifecycleState.choices,
        default=LifecycleState.ACTIVE
    )
    created_date       = models.DateField(null=True, blank=True,
                                          help_text='Document creation/issuance date')
    retention_due_date = models.DateField(null=True, blank=True,
                                          help_text='Calculated: created_date + retention_years')
    legal_hold_reason  = models.TextField(blank=True)
    legal_hold_by      = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True,
        on_delete=models.SET_NULL, related_name='legal_holds_placed'
    )
    legal_hold_at      = models.DateTimeField(null=True, blank=True)
    archived_at        = models.DateTimeField(null=True, blank=True)
    deleted_at         = models.DateTimeField(null=True, blank=True)
    deleted_by         = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True,
        on_delete=models.SET_NULL, related_name='documents_deleted'
    )
    notes              = models.TextField(blank=True)
    updated_at         = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'lifecycle_document'
        ordering = ['retention_due_date']

    def __str__(self):
        return f"{self.document.document_number} [{self.state}] due {self.retention_due_date}"


class LifecycleEvent(models.Model):
    """Immutable audit log of every lifecycle state transition."""

    document    = models.ForeignKey(Document, on_delete=models.CASCADE,
                                    related_name='lifecycle_events')
    from_state  = models.CharField(max_length=20, blank=True)
    to_state    = models.CharField(max_length=20)
    triggered_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True,
        on_delete=models.SET_NULL, related_name='lifecycle_events_triggered'
    )
    triggered_at = models.DateTimeField(auto_now_add=True)
    reason       = models.TextField(blank=True)

    class Meta:
        db_table = 'lifecycle_event'
        ordering = ['-triggered_at']

    def __str__(self):
        return (
            f"{self.document.document_number}: "
            f"{self.from_state} → {self.to_state} @ {self.triggered_at:%Y-%m-%d}"
        )

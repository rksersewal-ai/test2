"""LDO Work Ledger models - neutral record-keeping, no approval automation."""
from django.db import models
from django.conf import settings


class WorkType(models.Model):
    """Master table for LDO work types."""
    code = models.CharField(max_length=30, unique=True)
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'workflow_work_type'
        ordering = ['code']

    def __str__(self):
        return f"{self.code} - {self.name}"


class Vendor(models.Model):
    code = models.CharField(max_length=30, unique=True)
    name = models.CharField(max_length=200)
    address = models.TextField(blank=True)
    contact = models.CharField(max_length=100, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'workflow_vendor'
        ordering = ['name']

    def __str__(self):
        return self.name


class Tender(models.Model):
    class Status(models.TextChoices):
        OPEN = 'OPEN', 'Open'
        EVALUATION = 'EVALUATION', 'Under Evaluation'
        CLOSED = 'CLOSED', 'Closed'
        CANCELLED = 'CANCELLED', 'Cancelled'

    tender_number = models.CharField(max_length=100, unique=True, db_index=True)
    title = models.CharField(max_length=300)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.OPEN)
    issue_date = models.DateField(null=True, blank=True)
    closing_date = models.DateField(null=True, blank=True)
    eoffice_file_number = models.CharField(max_length=100, blank=True, db_index=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL, related_name='tenders_created')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'workflow_tender'
        ordering = ['-created_at']

    def __str__(self):
        return self.tender_number


class WorkLedger(models.Model):
    """Factual work record - no approval engine. Records what was done, when, by whom."""
    class Status(models.TextChoices):
        OPEN = 'OPEN', 'Open'
        IN_PROGRESS = 'IN_PROGRESS', 'In Progress'
        CLOSED = 'CLOSED', 'Closed'
        ON_HOLD = 'ON_HOLD', 'On Hold'

    work_type = models.ForeignKey(WorkType, null=True, on_delete=models.SET_NULL, related_name='work_ledger_entries')
    section = models.ForeignKey('core.Section', null=True, blank=True, on_delete=models.SET_NULL, related_name='work_ledger_entries')
    assigned_to = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name='work_ledger_assigned')
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.OPEN)

    # Key dates
    received_date = models.DateField(null=True, blank=True)
    target_date = models.DateField(null=True, blank=True)
    closed_date = models.DateField(null=True, blank=True)

    # eOffice reference (read-only reference, not approval logic)
    eoffice_file_number = models.CharField(max_length=100, blank=True, db_index=True)
    eoffice_subject = models.CharField(max_length=300, blank=True)

    # Linkages
    document = models.ForeignKey('edms.Document', null=True, blank=True, on_delete=models.SET_NULL, related_name='work_ledger_entries')
    revision = models.ForeignKey('edms.Revision', null=True, blank=True, on_delete=models.SET_NULL, related_name='work_ledger_entries')
    tender = models.ForeignKey(Tender, null=True, blank=True, on_delete=models.SET_NULL, related_name='work_ledger_entries')
    vendor = models.ForeignKey(Vendor, null=True, blank=True, on_delete=models.SET_NULL, related_name='work_ledger_entries')

    # Neutral remarks
    subject = models.CharField(max_length=300)
    remarks = models.TextField(blank=True)

    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL, related_name='work_ledger_created')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'workflow_work_ledger'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['eoffice_file_number']),
            models.Index(fields=['status', 'section']),
            models.Index(fields=['received_date', 'closed_date']),
        ]

    def __str__(self):
        return f"{self.subject} [{self.status}]"

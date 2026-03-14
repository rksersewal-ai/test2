# =============================================================================
# FILE: apps/work_ledger/models.py
# PRD Ref: Section 4.1 (Work Tracking), Section 12.4 (work_done_records index)
# =============================================================================
from django.db         import models
from django.conf       import settings
from django.utils      import timezone
from django.core.exceptions import ValidationError

User = settings.AUTH_USER_MODEL


# ---------------------------------------------------------------------------
# CHOICES
# ---------------------------------------------------------------------------
class WorkType(models.TextChoices):
    TENDER_PREPARATION    = 'TENDER_PREP',    'Tender Preparation'
    DRAWING_PROCESSING    = 'DRAWING_PROC',   'Drawing Processing / Alteration Update'
    SPEC_PROCESSING       = 'SPEC_PROC',      'Specification Processing'
    SDR_RESPONSE          = 'SDR',            'Shop Drawing Request (SDR) Response'
    TECH_EVALUATION       = 'TECH_EVAL',      'Technical Evaluation'
    INSPECTION_CALL       = 'INSP_CALL',      'Inspection Call Processing'
    IC_PROCESSING         = 'IC_PROC',        'Inspection Certificate Processing'
    SMI_IMPLEMENTATION    = 'SMI_IMPL',       'SMI Implementation'
    VENDOR_DRAWING_REVIEW = 'VDR_REVIEW',     'Vendor Drawing Review/Approval'
    ALTERATION_TRACKING   = 'ALT_TRACK',      'Alteration Tracking'
    PL_ENTRY              = 'PL_ENTRY',       'PL Number Data Entry'
    CORRESPONDENCE        = 'CORRESPONDENCE', 'Correspondence / Letter Processing'
    FILING                = 'FILING',         'Document Filing & Archiving'
    REPORT_PREPARATION    = 'REPORT',         'Report Preparation'
    MEETING               = 'MEETING',        'Meeting / Coordination'
    TRAINING              = 'TRAINING',       'Training'
    OTHER                 = 'OTHER',          'Other'


class WorkStatus(models.TextChoices):
    DRAFT      = 'DRAFT',      'Draft'
    SUBMITTED  = 'SUBMITTED',  'Submitted for Verification'
    VERIFIED   = 'VERIFIED',   'Verified by Supervisor'
    RETURNED   = 'RETURNED',   'Returned for Correction'
    APPROVED   = 'APPROVED',   'Approved'


class EffortUnit(models.TextChoices):
    HOURS    = 'HRS',   'Hours'
    QUANTITY = 'QTY',   'Quantity'
    PAGES    = 'PAGES', 'Pages'
    ITEMS    = 'ITEMS', 'Items'


class PriorityLevel(models.TextChoices):
    ROUTINE  = 'ROUTINE',  'Routine'
    URGENT   = 'URGENT',   'Urgent'
    CRITICAL = 'CRITICAL', 'Critical'


# ---------------------------------------------------------------------------
# WorkCategory
# Master list of work categories (admin-configurable)
# ---------------------------------------------------------------------------
class WorkCategory(models.Model):
    """Configurable category under which work entries are classified."""

    name         = models.CharField(max_length=100, unique=True)
    code         = models.CharField(max_length=20, unique=True)
    work_type    = models.CharField(
        max_length=30, choices=WorkType.choices, default=WorkType.OTHER
    )
    description  = models.TextField(blank=True)
    is_active    = models.BooleanField(default=True)
    sort_order   = models.PositiveSmallIntegerField(default=0)

    class Meta:
        db_table   = 'wl_work_category'
        ordering   = ['sort_order', 'name']
        verbose_name        = 'Work Category'
        verbose_name_plural = 'Work Categories'

    def __str__(self):
        return f'{self.code} – {self.name}'


# ---------------------------------------------------------------------------
# WorkEntry  (core table — PRD: work_done_records)
# ---------------------------------------------------------------------------
class WorkEntry(models.Model):
    """One unit of work done by a staff member on a given date."""

    # --- Who / When --------------------------------------------------------
    user         = models.ForeignKey(
        User, on_delete=models.PROTECT,
        related_name='work_entries',
        db_index=True,
    )
    work_date    = models.DateField(default=timezone.now, db_index=True)

    # --- Classification ----------------------------------------------------
    category     = models.ForeignKey(
        WorkCategory, on_delete=models.PROTECT,
        related_name='entries',
        null=True, blank=True,
    )
    work_type    = models.CharField(
        max_length=30, choices=WorkType.choices
    )
    priority     = models.CharField(
        max_length=10, choices=PriorityLevel.choices,
        default=PriorityLevel.ROUTINE,
    )

    # --- Description -------------------------------------------------------
    description  = models.TextField(
        help_text='Detailed description of work performed'
    )
    reference_number = models.CharField(
        max_length=150, blank=True,
        help_text='PL No / Drawing No / Tender No / SDR No / Case No etc.',
        db_index=True,
    )
    remarks      = models.TextField(blank=True)

    # --- Effort ------------------------------------------------------------
    effort_value = models.DecimalField(
        max_digits=7, decimal_places=2, null=True, blank=True,
        help_text='Numeric effort (hours / quantity / pages / items)',
    )
    effort_unit  = models.CharField(
        max_length=10, choices=EffortUnit.choices,
        default=EffortUnit.HOURS, blank=True,
    )

    # --- Links to domain objects (optional) --------------------------------
    linked_pl_number = models.ForeignKey(
        'pl_master.PLMaster',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='work_entries',
        to_field='pl_number',
    )
    linked_drawing_number = models.CharField(
        max_length=100, blank=True,
        help_text='CLW/BLW/RDSO drawing number if applicable',
    )
    linked_case_no = models.CharField(
        max_length=100, blank=True,
        help_text='Tender/case number if applicable',
    )
    linked_sdr_no  = models.CharField(
        max_length=100, blank=True,
        help_text='SDR number if applicable',
    )

    # --- Workflow status ---------------------------------------------------
    status       = models.CharField(
        max_length=15, choices=WorkStatus.choices,
        default=WorkStatus.DRAFT, db_index=True,
    )
    submitted_at = models.DateTimeField(null=True, blank=True)
    submitted_to = models.ForeignKey(
        User, on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='work_entries_to_verify',
    )

    # --- Audit -------------------------------------------------------------
    created_at   = models.DateTimeField(auto_now_add=True)
    updated_at   = models.DateTimeField(auto_now=True)

    class Meta:
        db_table  = 'wl_work_entry'
        ordering  = ['-work_date', '-created_at']
        indexes   = [
            models.Index(fields=['user', 'work_date'],   name='idx_wl_user_date'),
            models.Index(fields=['user', 'status'],      name='idx_wl_user_status'),
            models.Index(fields=['work_date', 'status'], name='idx_wl_date_status'),
            models.Index(fields=['reference_number'],    name='idx_wl_refnum'),
        ]
        verbose_name        = 'Work Entry'
        verbose_name_plural = 'Work Entries'

    def __str__(self):
        return f'{self.user} | {self.work_date} | {self.get_work_type_display()}'

    def clean(self):
        if self.work_date and self.work_date > timezone.now().date():
            raise ValidationError({'work_date': 'Work date cannot be in the future.'})

    # --- Workflow helpers --------------------------------------------------
    def can_submit(self):
        return self.status in (WorkStatus.DRAFT, WorkStatus.RETURNED)

    def can_verify(self):
        return self.status == WorkStatus.SUBMITTED

    def submit(self, supervisor):
        if not self.can_submit():
            raise ValidationError('Entry is not in a submittable state.')
        self.status       = WorkStatus.SUBMITTED
        self.submitted_at = timezone.now()
        self.submitted_to = supervisor
        self.save(update_fields=['status', 'submitted_at', 'submitted_to'])

    def return_for_correction(self, verifier, remarks):
        if not self.can_verify():
            raise ValidationError('Entry is not pending verification.')
        self.status = WorkStatus.RETURNED
        self.save(update_fields=['status'])
        WorkVerification.objects.create(
            work_entry=self,
            verifier=verifier,
            action=WorkVerification.Action.RETURNED,
            remarks=remarks,
        )


# ---------------------------------------------------------------------------
# WorkEntryAttachment
# ---------------------------------------------------------------------------
class WorkEntryAttachment(models.Model):
    """Supporting file attached to a work entry (e-Office letter, IC scan, etc.)."""

    work_entry   = models.ForeignKey(
        WorkEntry, on_delete=models.CASCADE,
        related_name='attachments',
    )
    file         = models.FileField(upload_to='work_ledger/attachments/%Y/%m/')
    file_name    = models.CharField(max_length=255)
    file_size    = models.PositiveIntegerField(help_text='Size in bytes')
    file_hash    = models.CharField(max_length=64, blank=True)
    description  = models.CharField(max_length=255, blank=True)
    uploaded_by  = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True
    )
    uploaded_at  = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'wl_entry_attachment'
        verbose_name        = 'Work Entry Attachment'
        verbose_name_plural = 'Work Entry Attachments'

    def __str__(self):
        return f'{self.file_name} → Entry#{self.work_entry_id}'


# ---------------------------------------------------------------------------
# WorkVerification
# ---------------------------------------------------------------------------
class WorkVerification(models.Model):
    """Supervisor verification / return action on a work entry."""

    class Action(models.TextChoices):
        VERIFIED = 'VERIFIED', 'Verified'
        RETURNED = 'RETURNED', 'Returned for Correction'
        APPROVED = 'APPROVED', 'Approved'

    work_entry   = models.ForeignKey(
        WorkEntry, on_delete=models.CASCADE,
        related_name='verifications',
    )
    verifier     = models.ForeignKey(
        User, on_delete=models.PROTECT,
        related_name='work_verifications',
    )
    action       = models.CharField(max_length=15, choices=Action.choices)
    remarks      = models.TextField(blank=True)
    verified_at  = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'wl_work_verification'
        ordering = ['-verified_at']
        verbose_name        = 'Work Verification'
        verbose_name_plural = 'Work Verifications'

    def __str__(self):
        return f'{self.verifier} → {self.action} | Entry#{self.work_entry_id}'


# ---------------------------------------------------------------------------
# WorkTarget
# Monthly / weekly targets set by supervisors for each user
# ---------------------------------------------------------------------------
class WorkTarget(models.Model):
    """Performance target assigned to a staff member for a calendar period."""

    class PeriodType(models.TextChoices):
        DAILY   = 'DAILY',   'Daily'
        WEEKLY  = 'WEEKLY',  'Weekly'
        MONTHLY = 'MONTHLY', 'Monthly'

    user          = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='work_targets',
    )
    set_by        = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True,
        related_name='targets_set',
    )
    period_type   = models.CharField(
        max_length=10, choices=PeriodType.choices,
        default=PeriodType.MONTHLY,
    )
    period_start  = models.DateField()
    period_end    = models.DateField()
    work_type     = models.CharField(
        max_length=30, choices=WorkType.choices, blank=True,
        help_text='Leave blank for overall target',
    )
    target_value  = models.DecimalField(max_digits=8, decimal_places=2)
    target_unit   = models.CharField(
        max_length=10, choices=EffortUnit.choices, default=EffortUnit.ITEMS
    )
    description   = models.TextField(blank=True)
    is_active     = models.BooleanField(default=True)
    created_at    = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'wl_work_target'
        ordering = ['-period_start']
        verbose_name        = 'Work Target'
        verbose_name_plural = 'Work Targets'

    def __str__(self):
        return f'Target: {self.user} | {self.period_start} – {self.period_end}'

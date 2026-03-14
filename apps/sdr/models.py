# =============================================================================
# FILE: apps/sdr/models.py
#
# Shop Drawing Request (SDR) lifecycle models
#
# WORKFLOW:
#   DRAFT → SUBMITTED → ASSIGNED → IN_PROGRESS → RESPONDED → CLOSED
#                          └→ REJECTED (invalid/duplicate)
#                          └→ ESCALATED (overdue / shop re-raises)
# =============================================================================
from django.db   import models
from django.conf import settings


# ---------------------------------------------------------------------------
SDR_STATUS = [
    ('DRAFT',       'Draft'),
    ('SUBMITTED',   'Submitted'),
    ('ASSIGNED',    'Assigned'),
    ('IN_PROGRESS', 'In Progress'),
    ('RESPONDED',   'Responded'),
    ('ESCALATED',   'Escalated'),
    ('CLOSED',      'Closed'),
    ('REJECTED',    'Rejected'),
]

SHOP_SECTION = [
    ('MECH', 'Mechanical Shop'),
    ('ELEC', 'Electrical Shop'),
    ('BOGIE','Bogie Shop'),
    ('PAINT','Paint Shop'),
    ('WELDING','Welding Shop'),
    ('MACHINING','Machining Shop'),
    ('ASSEMBLY','Assembly Shop'),
    ('QC',  'Quality Control'),
    ('STORE','Stores Section'),
    ('OTHER','Other'),
]

URGENCY = [
    ('ROUTINE',   'Routine'),
    ('URGENT',    'Urgent'),
    ('CRITICAL',  'Critical / Production Hold'),
]

CLARIFICATION_TYPE = [
    ('DRG_COPY',      'Drawing Copy Required'),
    ('DRG_CLARITY',   'Drawing Clarity Issue'),
    ('DIM_QUERY',     'Dimensional Query'),
    ('MAT_QUERY',     'Material / Specification Query'),
    ('FIT_ISSUE',     'Fitment / Assembly Issue'),
    ('DEVIATION',     'Deviation Request'),
    ('CONCESSION',    'Concession Request'),
    ('ALT_INFO',      'Alteration Information'),
    ('SMI_INFO',      'SMI Clarification'),
    ('OTHER',         'Other'),
]


# ===========================================================================
class SDRRequest(models.Model):
    """
    Core SDR record raised by a shop user.
    """
    # Auto SDR number: SDR/YYYY-YY/NNNNN
    sdr_number          = models.CharField(max_length=30, unique=True, blank=True)

    # Raised-by
    raised_by           = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT,
        related_name='sdr_raised', verbose_name='Raised By'
    )
    raising_section     = models.CharField(max_length=20, choices=SHOP_SECTION, default='MECH')
    loco_number         = models.CharField(max_length=30, blank=True, help_text='Loco no. under work')
    loco_type           = models.CharField(max_length=20, blank=True, help_text='WAG9/WAP7/etc')

    # Drawing / PL reference
    drawing_number      = models.CharField(max_length=100, blank=True)
    pl_number           = models.CharField(max_length=50,  blank=True)
    sub_assembly        = models.CharField(max_length=200, blank=True)

    # Query
    clarification_type  = models.CharField(max_length=30, choices=CLARIFICATION_TYPE, default='OTHER')
    subject             = models.CharField(max_length=500)
    query_description   = models.TextField()
    urgency             = models.CharField(max_length=20, choices=URGENCY, default='ROUTINE')

    # Scheduling
    required_by_date    = models.DateField(null=True, blank=True)
    production_hold     = models.BooleanField(default=False, help_text='Production line stopped?')

    # Workflow
    status              = models.CharField(max_length=20, choices=SDR_STATUS, default='DRAFT')
    assigned_to         = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='sdr_assigned'
    )
    assigned_by         = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='sdr_assigned_by'
    )
    assigned_at         = models.DateTimeField(null=True, blank=True)
    target_response_date= models.DateField(null=True, blank=True)

    # Resolution
    is_duplicate        = models.BooleanField(default=False)
    duplicate_of        = models.ForeignKey(
        'self', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='duplicates'
    )
    rejection_reason    = models.TextField(blank=True)

    # Close
    closed_by           = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='sdr_closed'
    )
    closed_at           = models.DateTimeField(null=True, blank=True)
    closure_remarks     = models.TextField(blank=True)
    shop_satisfaction   = models.PositiveSmallIntegerField(
        null=True, blank=True,
        help_text='Shop satisfaction rating 1-5'
    )

    # Timestamps
    created_at          = models.DateTimeField(auto_now_add=True)
    updated_at          = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'sdr_request'
        ordering = ['-created_at']
        indexes  = [
            models.Index(fields=['sdr_number']),
            models.Index(fields=['status']),
            models.Index(fields=['drawing_number']),
            models.Index(fields=['pl_number']),
            models.Index(fields=['assigned_to', 'status']),
        ]

    def __str__(self):
        return f'{self.sdr_number} — {self.subject[:60]}'

    def save(self, *args, **kwargs):
        if not self.sdr_number:
            self.sdr_number = self._generate_sdr_number()
        super().save(*args, **kwargs)

    @classmethod
    def _generate_sdr_number(cls):
        from django.utils import timezone
        now   = timezone.now()
        year  = now.year
        yr2   = str(year)[-2:]
        yr2n  = str(year + 1)[-2:]
        prefix = f'SDR/{year}-{yr2n}'
        last  = (
            cls.objects
            .filter(sdr_number__startswith=prefix)
            .order_by('-sdr_number')
            .first()
        )
        seq = 1
        if last:
            try:
                seq = int(last.sdr_number.split('/')[-1]) + 1
            except (ValueError, IndexError):
                seq = cls.objects.filter(sdr_number__startswith=prefix).count() + 1
        return f'{prefix}/{seq:05d}'


# ===========================================================================
class SDRResponse(models.Model):
    """
    LDO technical response to an SDR (can be multiple interim + final).
    """
    RESPONSE_TYPE = [
        ('INTERIM', 'Interim / Partial Response'),
        ('FINAL',   'Final Response'),
    ]

    sdr_request     = models.ForeignKey(
        SDRRequest, on_delete=models.CASCADE, related_name='responses'
    )
    response_type   = models.CharField(max_length=10, choices=RESPONSE_TYPE, default='FINAL')
    responded_by    = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT,
        related_name='sdr_responses'
    )

    # Response content
    technical_response  = models.TextField()
    clarified_drawing   = models.CharField(max_length=100, blank=True)
    clarified_alteration= models.CharField(max_length=20,  blank=True)
    dimension_reference = models.TextField(blank=True, help_text='Relevant dimensions / table ref')
    action_required     = models.TextField(blank=True, help_text='Any action required by shop')

    # Linked SMI / deviation
    linked_smi          = models.CharField(max_length=100, blank=True)
    deviation_permitted = models.BooleanField(default=False)
    concession_reference= models.CharField(max_length=100, blank=True)

    # e-Office reference
    eoffice_file_no     = models.CharField(max_length=100, blank=True)

    responded_at        = models.DateTimeField(auto_now_add=True)
    updated_at          = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'sdr_response'
        ordering = ['responded_at']

    def __str__(self):
        return f'Response to {self.sdr_request.sdr_number} ({self.response_type})'


# ===========================================================================
class SDRAttachment(models.Model):
    """
    Supporting file attached to an SDR request or response.
    """
    ATTACHED_TO = [
        ('REQUEST',  'SDR Request'),
        ('RESPONSE', 'SDR Response'),
    ]

    attached_to_type= models.CharField(max_length=10, choices=ATTACHED_TO)
    sdr_request     = models.ForeignKey(
        SDRRequest, on_delete=models.CASCADE, related_name='attachments'
    )
    sdr_response    = models.ForeignKey(
        SDRResponse, on_delete=models.CASCADE,
        null=True, blank=True, related_name='attachments'
    )
    uploaded_by     = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT,
        related_name='sdr_attachments'
    )

    file            = models.FileField(upload_to='sdr/%Y/%m/')
    file_name       = models.CharField(max_length=200)
    file_size       = models.BigIntegerField()
    description     = models.CharField(max_length=300, blank=True)

    uploaded_at     = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'sdr_attachment'

    def __str__(self):
        return f'{self.file_name} → {self.sdr_request.sdr_number}'

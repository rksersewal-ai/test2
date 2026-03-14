# =============================================================================
# FILE: apps/sdr/models.py
#
# SDR = Shop Drawing / Specification Issue Register
#
# Purpose:
#   Record every issue of a drawing or specification print to a shop.
#   No approval workflow. Pure register / ledger.
#
# Two tables:
#   SDRRecord  — one record per issue transaction (one shop, one day, one request)
#   SDRItem    — one row per drawing/spec issued in that transaction
# =============================================================================
from django.db   import models
from django.conf import settings


DRAWING_SIZES = [
    ('A0', 'A0'),
    ('A1', 'A1'),
    ('A2', 'A2'),
    ('A3', 'A3'),
    ('A4', 'A4'),
]

DOC_TYPE_CHOICES = [
    ('DRAWING', 'Drawing'),
    ('SPEC',    'Specification'),
]


class SDRRecord(models.Model):
    """
    Header: one issue transaction.
    """
    # Auto-generated register number: SDR/2026-27/00001
    sdr_number = models.CharField(max_length=30, unique=True, editable=False)

    issue_date          = models.DateField()
    shop_name           = models.CharField(max_length=120)
    requesting_official = models.CharField(max_length=120, help_text='Name of official requesting the prints')
    issuing_official    = models.CharField(max_length=120, help_text='Name of LDO staff issuing the prints')
    receiving_official  = models.CharField(max_length=120, help_text='Name of official who physically received the prints')

    remarks = models.TextField(blank=True)

    # Audit
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='sdr_records_created',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering     = ['-issue_date', '-created_at']
        verbose_name = 'SDR Record'
        verbose_name_plural = 'SDR Records'

    def __str__(self):
        return f'{self.sdr_number} | {self.shop_name} | {self.issue_date}'

    def save(self, *args, **kwargs):
        if not self.sdr_number:
            self.sdr_number = self._generate_sdr_number()
        super().save(*args, **kwargs)

    @staticmethod
    def _generate_sdr_number():
        from django.utils import timezone
        today     = timezone.localdate()
        fy_start  = today.year if today.month >= 4 else today.year - 1
        fy_label  = f'{fy_start}-{str(fy_start + 1)[2:]}'
        prefix    = f'SDR/{fy_label}/'
        last = (
            SDRRecord.objects
            .filter(sdr_number__startswith=prefix)
            .order_by('-sdr_number')
            .first()
        )
        seq = 1
        if last:
            try:
                seq = int(last.sdr_number.split('/')[-1]) + 1
            except (ValueError, IndexError):
                pass
        return f'{prefix}{seq:05d}'

    # Convenience
    @property
    def total_items(self):
        return self.items.count()

    @property
    def has_controlled_copy(self):
        return self.items.filter(controlled_copy=True).exists()


class SDRItem(models.Model):
    """
    Line item: one drawing or specification per row.
    """
    sdr_record = models.ForeignKey(
        SDRRecord,
        on_delete=models.CASCADE,
        related_name='items',
    )

    # Document type + FK search
    document_type   = models.CharField(max_length=10, choices=DOC_TYPE_CHOICES, default='DRAWING')

    # Resolved FKs (set when user picks from search)
    drawing         = models.ForeignKey(
        'pl_master.DrawingMaster',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='sdr_issues',
    )
    specification   = models.ForeignKey(
        'pl_master.SpecificationMaster',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='sdr_issues',
    )

    # Denormalised display fields (populated from FK on save)
    document_number = models.CharField(max_length=80)   # e.g. CLW/M/WAP7-1234
    document_title  = models.CharField(max_length=255, blank=True)
    alteration_no   = models.CharField(max_length=20,  blank=True, help_text='Current alteration at time of issue')

    # Issue details
    size            = models.CharField(max_length=4, choices=DRAWING_SIZES, default='A1')
    copies          = models.PositiveSmallIntegerField(default=1)
    controlled_copy = models.BooleanField(
        default=False,
        help_text='Tick if this is a Controlled Copy (stamp applied)'
    )

    class Meta:
        ordering     = ['id']
        verbose_name = 'SDR Item'

    def __str__(self):
        return f'{self.document_number} | {self.size} x{self.copies}'

    def save(self, *args, **kwargs):
        # Auto-populate denormalised fields from FK
        if self.drawing and self.document_type == 'DRAWING':
            self.document_number = self.drawing.drawing_number
            self.document_title  = self.drawing.drawing_title or ''
            self.alteration_no   = self.drawing.current_alteration or ''
        elif self.specification and self.document_type == 'SPEC':
            self.document_number = self.specification.spec_number
            self.document_title  = self.specification.spec_title or ''
            self.alteration_no   = self.specification.current_alteration or ''
        super().save(*args, **kwargs)

# =============================================================================
# FILE: backend/master/models_pl_docs.py
# MODELS for PL Master extended features:
#   1. PLVendorInfo       — VD / NVD selection + UVAM VD number / eligibility
#   2. PLLinkedDocument   — M2M link between a PL Number and any EDMS document
#                           (up to 100 per PL)
# =============================================================================
from django.db import models
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model

User = get_user_model()


# ─────────────────────────────────────────────────────────────────────────────
# 1. VD / NVD Vendor Info
# ─────────────────────────────────────────────────────────────────────────────
class PLVendorInfo(models.Model):
    """
    Stores Vendor Directory (VD) or Non-Vendor Directory (NVD) information
    for a PL Number.
    - If VD  : store the UVAM Vendor Directory number.
    - If NVD : store free-text eligibility criteria (max 2000 words).
    One record per PL number (OneToOne pattern via pl_number CharField).
    """
    VENDOR_TYPE_CHOICES = [
        ('VD',  'VD — Vendor Directory (UVAM)'),
        ('NVD', 'NVD — Non-Vendor Directory'),
    ]

    pl_number        = models.CharField(max_length=50, unique=True, db_index=True)
    vendor_type      = models.CharField(
        max_length=3, choices=VENDOR_TYPE_CHOICES, default='NVD'
    )
    # VD fields
    uvam_vd_number   = models.CharField(
        max_length=60, blank=True,
        help_text='UVAM Vendor Directory Number (required when vendor_type = VD)'
    )
    # NVD fields
    eligibility_criteria = models.TextField(
        blank=True,
        help_text='Eligibility criteria for non-VD sourcing (max 2000 words)'
    )
    # Audit
    updated_by   = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='pl_vendor_updates'
    )
    updated_at   = models.DateTimeField(auto_now=True)
    created_at   = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label  = 'master'
        ordering   = ['pl_number']
        verbose_name = 'PL Vendor / Eligibility Info'

    def __str__(self):
        return f'{self.pl_number} [{self.vendor_type}]'

    def clean(self):
        if self.vendor_type == 'VD' and not self.uvam_vd_number.strip():
            raise ValidationError({'uvam_vd_number': 'UVAM VD Number is required for VD parts.'})
        if self.vendor_type == 'NVD':
            word_count = len(self.eligibility_criteria.split())
            if word_count > 2000:
                raise ValidationError(
                    {'eligibility_criteria':
                     f'Eligibility criteria must not exceed 2000 words (current: {word_count}).'
                    }
                )


# ─────────────────────────────────────────────────────────────────────────────
# 2. PL Linked Document  (up to 100 per PL)
# ─────────────────────────────────────────────────────────────────────────────
DOC_CATEGORY_CHOICES = [
    ('SPECIFICATION', 'Specification'),
    ('DRAWING',       'Drawing'),
    ('STANDARD',      'Standard'),
    ('STR',           'STR — Special Technical Requirement'),
    ('TECH_EVAL',     'Technical Evaluation Document'),
    ('OTHER',         'Other Technical Document'),
]


def _validate_max_100(pl_number, instance_pk=None):
    qs = PLLinkedDocument.objects.filter(pl_number=pl_number)
    if instance_pk:
        qs = qs.exclude(pk=instance_pk)
    if qs.count() >= 100:
        raise ValidationError(
            'Maximum 100 documents can be linked to a single PL Number.'
        )


class PLLinkedDocument(models.Model):
    """
    Links an existing EDMS document (by document_id) to a PL Number.
    Also supports uploaded tech-eval docs (cross-referenced via tech_eval_doc_id).
    Category drives the accordion section it appears in on the UI.
    """
    pl_number      = models.CharField(max_length=50, db_index=True)
    # Reference to the main EDMS document (nullable for tech-eval cross-links)
    document_id    = models.PositiveIntegerField(
        null=True, blank=True,
        help_text='ID of the linked EDMS Document record'
    )
    # Denormalised for fast display without joining to the document table
    document_title = models.CharField(max_length=300, blank=True)
    document_number= models.CharField(max_length=120, blank=True)
    category       = models.CharField(
        max_length=20, choices=DOC_CATEGORY_CHOICES, default='OTHER'
    )
    remarks        = models.CharField(max_length=200, blank=True)
    linked_by      = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='pl_doc_links'
    )
    linked_at      = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label      = 'master'
        ordering       = ['category', 'document_number']
        unique_together = [['pl_number', 'document_id']]
        verbose_name   = 'PL Linked Document'
        indexes = [
            models.Index(fields=['pl_number', 'category']),
        ]

    def __str__(self):
        return f'{self.pl_number} ↔ {self.document_number or self.document_id}'

    def save(self, *args, **kwargs):
        if not self.pk:
            _validate_max_100(self.pl_number)
        super().save(*args, **kwargs)

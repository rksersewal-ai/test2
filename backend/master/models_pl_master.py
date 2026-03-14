# =============================================================================
# FILE: backend/master/models_pl_master.py
# MODEL: PLMasterItem  —  the core PL Number master record
# This is the primary entity that PLVendorInfo, PLLinkedDocument,
# and PLTechEvalDocument all reference via pl_number CharField.
# =============================================================================
from django.db import models
from django.conf import settings


LOCO_TYPE_CHOICES = [
    ('WAG9',   'WAG9'),   ('WAG9H',  'WAG9H'),  ('WAG12B', 'WAG12B'),
    ('WAP7',   'WAP7'),   ('WAP5',   'WAP5'),
    ('DETC',   'DETC'),   ('MEMU',   'MEMU'),    ('DEMU',   'DEMU'),
    ('WDG4',   'WDG4'),   ('WDP4',   'WDP4'),    ('OTHER',  'Other'),
]

INSPECTION_CATEGORY_CHOICES = [
    ('A', 'A — Safety Critical'),
    ('B', 'B — Important'),
    ('C', 'C — Normal'),
]


class PLMasterItem(models.Model):
    """
    Part List (PL) Master Item.
    pl_number is the business key (e.g. PL/EL/WAG9/0042).
    """
    pl_number            = models.CharField(max_length=50, unique=True, db_index=True)
    description          = models.CharField(max_length=300, blank=True)
    uvam_id              = models.CharField(max_length=60, blank=True, help_text='UVAM item ID')
    inspection_category  = models.CharField(
        max_length=1, choices=INSPECTION_CATEGORY_CHOICES, blank=True
    )
    safety_item          = models.BooleanField(default=False)
    loco_types           = models.JSONField(default=list, blank=True,
                             help_text='List of applicable loco type codes')
    application_area     = models.CharField(max_length=200, blank=True)
    used_in              = models.CharField(max_length=200, blank=True)
    is_active            = models.BooleanField(default=True)
    remarks              = models.TextField(blank=True)

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL,
        related_name='pl_items_created'
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL,
        related_name='pl_items_updated'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label  = 'master'
        ordering   = ['pl_number']
        verbose_name = 'PL Master Item'
        verbose_name_plural = 'PL Master Items'
        indexes = [
            models.Index(fields=['pl_number']),
            models.Index(fields=['inspection_category']),
            models.Index(fields=['safety_item']),
        ]

    def __str__(self):
        return f'{self.pl_number} — {self.description[:60]}'

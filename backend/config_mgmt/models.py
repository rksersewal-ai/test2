# =============================================================================
# FILE: backend/config_mgmt/models.py
# LocoConfig — locomotive configuration register
# ECN        — Engineering Change Notice register
# =============================================================================
from django.db import models
from django.conf import settings


COMMON_STATUS = [
    ('PENDING',    'Pending'),
    ('APPROVED',   'Approved'),
    ('SUPERSEDED', 'Superseded'),
    ('REJECTED',   'Rejected'),
]

LOCO_CLASSES = [
    ('WAG-9',   'WAG-9'),
    ('WAG-9H',  'WAG-9H'),
    ('WAG-9HH', 'WAG-9HH'),
    ('WAP-7',   'WAP-7'),
    ('WAP-5',   'WAP-5'),
    ('WAG-12B', 'WAG-12B'),
    ('MEMU',    'MEMU'),
    ('DEMU',    'DEMU'),
]


class LocoConfig(models.Model):
    """Locomotive configuration version record — one row per loco serial + config version."""
    loco_class      = models.CharField(max_length=20, choices=LOCO_CLASSES)
    serial_no       = models.CharField(max_length=20)
    config_version  = models.CharField(max_length=20)
    ecn_ref         = models.CharField(max_length=60, blank=True)
    effective_date  = models.DateField(null=True, blank=True)
    changed_by      = models.CharField(max_length=100, blank=True,
                                        help_text='CLW Engineering / RDSO / ABB')
    status          = models.CharField(max_length=20, choices=COMMON_STATUS, default='PENDING')
    remarks         = models.TextField(blank=True)
    created_by      = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True,
        on_delete=models.SET_NULL, related_name='loco_configs_created'
    )
    created_at      = models.DateTimeField(auto_now_add=True)
    updated_at      = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Loco Configuration'
        verbose_name_plural = 'Loco Configurations'
        unique_together = [['serial_no', 'config_version']]

    def __str__(self):
        return f'{self.loco_class} / {self.serial_no} — v{self.config_version}'


class ECN(models.Model):
    """Engineering Change Notice — controls modifications to loco configurations."""
    ecn_number    = models.CharField(max_length=40, unique=True)
    subject       = models.CharField(max_length=200)
    loco_class    = models.CharField(max_length=20, choices=LOCO_CLASSES, blank=True)
    description   = models.TextField(blank=True)
    status        = models.CharField(max_length=20, choices=COMMON_STATUS, default='PENDING')
    date          = models.DateField(null=True, blank=True)
    raised_by     = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True,
        on_delete=models.SET_NULL, related_name='ecns_raised'
    )
    approved_by   = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True,
        on_delete=models.SET_NULL, related_name='ecns_approved'
    )
    approved_at   = models.DateTimeField(null=True, blank=True)
    affected_configs = models.ManyToManyField(LocoConfig, blank=True, related_name='ecns')
    remarks       = models.TextField(blank=True)
    created_at    = models.DateTimeField(auto_now_add=True)
    updated_at    = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Engineering Change Notice'
        verbose_name_plural = 'ECN Register'

    def __str__(self):
        return f'{self.ecn_number} — {self.subject}'

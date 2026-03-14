# =============================================================================
# FILE: backend/prototype/models.py
# Inspection  — inspection record (prototype / periodic / special / PDI / RTS)
# PunchItem   — individual defect/observation within an inspection
# =============================================================================
from django.db import models
from django.conf import settings


INSPECTION_TYPES = [
    ('Prototype',         'Prototype'),
    ('Periodic',          'Periodic'),
    ('Special',           'Special'),
    ('PDI',               'PDI (Pre-Delivery Inspection)'),
    ('ReturnToService',   'Return to Service'),
]

INSPECTION_STATUS = [
    ('Open',        'Open'),
    ('In Progress', 'In Progress'),
    ('Pass',        'Pass'),
    ('Fail',        'Fail'),
    ('Closed',      'Closed'),
]

PUNCH_STATUS = [
    ('Open',   'Open'),
    ('Closed', 'Closed'),
]


class Inspection(models.Model):
    loco_number      = models.CharField(max_length=20)
    loco_class       = models.CharField(max_length=20)
    inspection_type  = models.CharField(max_length=30, choices=INSPECTION_TYPES)
    inspection_date  = models.DateField()
    inspector        = models.CharField(max_length=100)
    status           = models.CharField(max_length=20, choices=INSPECTION_STATUS, default='Open')
    remarks          = models.TextField(blank=True)
    created_by       = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True,
        on_delete=models.SET_NULL, related_name='inspections_created'
    )
    created_at       = models.DateTimeField(auto_now_add=True)
    updated_at       = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-inspection_date', '-created_at']
        verbose_name = 'Inspection'
        verbose_name_plural = 'Inspections'

    def __str__(self):
        return f'{self.inspection_type} — {self.loco_class}/{self.loco_number} ({self.inspection_date})'

    @property
    def open_punch_count(self):
        return self.punch_items.filter(status='Open').count()


class PunchItem(models.Model):
    inspection   = models.ForeignKey(Inspection, on_delete=models.CASCADE, related_name='punch_items')
    description  = models.TextField()
    status       = models.CharField(max_length=10, choices=PUNCH_STATUS, default='Open')
    raised_by    = models.CharField(max_length=100, blank=True)
    closed_by    = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True,
        on_delete=models.SET_NULL, related_name='punch_items_closed'
    )
    closed_at    = models.DateTimeField(null=True, blank=True)
    remarks      = models.TextField(blank=True)
    created_at   = models.DateTimeField(auto_now_add=True)
    updated_at   = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['created_at']
        verbose_name = 'Punch Item'
        verbose_name_plural = 'Punch Items'

    def __str__(self):
        return f'#{self.pk} [{self.status}] — {self.description[:60]}'

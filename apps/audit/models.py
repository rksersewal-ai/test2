"""Immutable audit log model.

Design rules (PRD §20.4):
- Rows are INSERT-only. No update/delete via ORM.
- Enforced at DB level via a trigger (see migration 0002).
- Django admin: read-only registration.
"""
from django.db import models
from django.conf import settings


class AuditLog(models.Model):
    """System-wide immutable activity record."""

    class Module(models.TextChoices):
        EDMS     = 'EDMS',     'EDMS'
        WORKFLOW = 'WORKFLOW', 'Work Ledger'
        OCR      = 'OCR',      'OCR Pipeline'
        CORE     = 'CORE',     'Core / Admin'
        AUTH     = 'AUTH',     'Authentication'

    timestamp       = models.DateTimeField(auto_now_add=True, db_index=True)
    user            = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='audit_logs',
    )
    username        = models.CharField(max_length=150, blank=True)   # snapshot at log time
    user_full_name  = models.CharField(max_length=300, blank=True)

    module          = models.CharField(max_length=20, choices=Module.choices, db_index=True)
    action          = models.CharField(max_length=80, db_index=True)

    entity_type     = models.CharField(max_length=80, blank=True)
    entity_id       = models.BigIntegerField(null=True, blank=True)
    entity_identifier = models.CharField(max_length=300, blank=True)

    description     = models.TextField(blank=True)
    extra_data      = models.JSONField(null=True, blank=True)   # optional structured payload

    ip_address      = models.GenericIPAddressField(null=True, blank=True)
    user_agent      = models.CharField(max_length=500, blank=True)
    success         = models.BooleanField(default=True)

    class Meta:
        db_table = 'audit_log'
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['module', 'action']),
            models.Index(fields=['entity_type', 'entity_id']),
            models.Index(fields=['user']),
            models.Index(fields=['timestamp']),
        ]

    def save(self, *args, **kwargs):
        if self.pk is not None:
            raise ValueError('AuditLog records are immutable and cannot be updated.')
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        raise ValueError('AuditLog records cannot be deleted.')

    def __str__(self):
        return f'[{self.module}] {self.action} by {self.username} at {self.timestamp}'

"""Immutable audit log models - no update/delete. Insert-only by design."""
from django.db import models
from django.conf import settings


class AuditLog(models.Model):
    """Append-only audit log. Never update or delete rows."""
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL, related_name='audit_logs')
    username = models.CharField(max_length=60, db_index=True)
    action = models.CharField(max_length=50, db_index=True)
    module = models.CharField(max_length=50, db_index=True)
    entity_type = models.CharField(max_length=100)
    entity_id = models.CharField(max_length=50, blank=True)
    entity_identifier = models.CharField(max_length=300, blank=True)
    description = models.TextField(blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.CharField(max_length=500, blank=True)
    request_method = models.CharField(max_length=10, blank=True)
    request_path = models.CharField(max_length=500, blank=True)
    before_value = models.JSONField(null=True, blank=True)
    after_value = models.JSONField(null=True, blank=True)
    changes = models.JSONField(null=True, blank=True)
    success = models.BooleanField(default=True)
    error_message = models.TextField(blank=True)
    session_id = models.CharField(max_length=100, blank=True)

    class Meta:
        db_table = 'audit_log'
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['timestamp', 'module']),
            models.Index(fields=['username', 'action']),
            models.Index(fields=['entity_type', 'entity_id']),
        ]

    def save(self, *args, **kwargs):
        # Enforce insert-only: no updates to existing rows
        if self.pk:
            raise PermissionError('Audit log entries are immutable and cannot be updated.')
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        raise PermissionError('Audit log entries cannot be deleted.')


class DocumentAccessLog(models.Model):
    """Records every document or file access event."""
    class AccessType(models.TextChoices):
        VIEW = 'VIEW', 'View'
        DOWNLOAD = 'DOWNLOAD', 'Download'
        SEARCH = 'SEARCH', 'Search'
        UPLOAD = 'UPLOAD', 'Upload'

    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL, related_name='doc_access_logs')
    document_id = models.IntegerField(null=True, blank=True, db_index=True)
    revision_id = models.IntegerField(null=True, blank=True)
    file_id = models.IntegerField(null=True, blank=True)
    access_type = models.CharField(max_length=20, choices=AccessType.choices)
    document_number = models.CharField(max_length=100, blank=True, db_index=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    session_id = models.CharField(max_length=100, blank=True)

    class Meta:
        db_table = 'audit_document_access_log'
        ordering = ['-timestamp']

    def save(self, *args, **kwargs):
        if self.pk:
            raise PermissionError('Document access log entries are immutable.')
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        raise PermissionError('Document access log entries cannot be deleted.')

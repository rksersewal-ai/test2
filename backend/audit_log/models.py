# =============================================================================
# FILE: backend/audit_log/models.py
# AuditLog — system-wide action audit trail
# =============================================================================
from django.db import models
from django.conf import settings


ACTION_CHOICES = [
    ('CREATE', 'Create'), ('UPDATE', 'Update'),   ('DELETE', 'Delete'),
    ('VIEW',   'View'),   ('APPROVE', 'Approve'),  ('REJECT', 'Reject'),
    ('LOGIN',  'Login'),  ('LOGOUT', 'Logout'),    ('EXPORT', 'Export'),
]


class AuditLog(models.Model):
    user        = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True,
        on_delete=models.SET_NULL, related_name='audit_logs'
    )
    action      = models.CharField(max_length=20, choices=ACTION_CHOICES)
    model       = models.CharField(max_length=60, blank=True, help_text='Django model name')
    object_id   = models.CharField(max_length=40, blank=True)
    object_repr = models.CharField(max_length=200, blank=True)
    changes     = models.JSONField(null=True, blank=True,
                                   help_text='Dict of {field: [old, new]} for UPDATE actions')
    description = models.TextField(blank=True)
    ip_address  = models.GenericIPAddressField(null=True, blank=True)
    timestamp   = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ['-timestamp']
        verbose_name = 'Audit Log'
        verbose_name_plural = 'Audit Logs'

    def __str__(self):
        return f'{self.timestamp:%Y-%m-%d %H:%M} | {self.user} | {self.action} | {self.model}/{self.object_id}'


def log_action(user, action, model='', object_id='', object_repr='',
               changes=None, description='', request=None):
    """Helper to create an AuditLog entry from anywhere in the codebase."""
    ip = None
    if request:
        xff = request.META.get('HTTP_X_FORWARDED_FOR')
        ip  = xff.split(',')[0].strip() if xff else request.META.get('REMOTE_ADDR')
    AuditLog.objects.create(
        user=user if (user and user.is_authenticated) else None,
        action=action, model=model, object_id=str(object_id),
        object_repr=object_repr, changes=changes,
        description=description, ip_address=ip,
    )

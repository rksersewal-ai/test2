# =============================================================================
# FILE: apps/notifications/models.py
# SPRINT 4 — In-App Notification Inbox
# =============================================================================
from django.db import models
from django.conf import settings


class Notification(models.Model):
    class Kind(models.TextChoices):
        INFO                 = 'INFO',                 'Info'
        SUCCESS              = 'SUCCESS',              'Success'
        WARNING              = 'WARNING',              'Warning'
        ERROR                = 'ERROR',                'Error'
        APPROVAL_REQUESTED   = 'APPROVAL_REQUESTED',   'Approval Requested'
        APPROVAL_VOTED       = 'APPROVAL_VOTED',       'Approval Voted'
        APPROVAL_APPROVED    = 'APPROVAL_APPROVED',    'Approval Approved'
        APPROVAL_REJECTED    = 'APPROVAL_REJECTED',    'Approval Rejected'
        OVERDUE_WORK         = 'OVERDUE_WORK',         'Overdue Work'
        OCR_COMPLETE         = 'OCR_COMPLETE',         'OCR Complete'
        OCR_FAILED           = 'OCR_FAILED',           'OCR Failed'
        DOCUMENT_PUBLISHED   = 'DOCUMENT_PUBLISHED',   'Document Published'
        MENTION              = 'MENTION',              'Mention'

    user       = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='notifications'
    )
    kind       = models.CharField(max_length=40, choices=Kind.choices,
                     default=Kind.INFO, db_index=True)
    title      = models.CharField(max_length=300)
    body       = models.TextField(blank=True)
    action_url = models.CharField(max_length=500, blank=True,
                     help_text='Frontend route to navigate to on click.')
    is_read    = models.BooleanField(default=False, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    expires_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'notification_inbox'
        ordering = ['-created_at']
        indexes  = [
            models.Index(
                fields=['user', 'is_read', '-created_at'],
                name='idx_notif_user_unread',
                condition=models.Q(is_read=False),
            ),
            models.Index(fields=['user', '-created_at'],
                         name='idx_notif_user_all'),
        ]

    def __str__(self):
        return f'[{self.kind}] {self.title} → {self.user}'

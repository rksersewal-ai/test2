# =============================================================================
# FILE: apps/notifications/services.py
# SPRINT 4 — NotificationService
# Low-level service called by ApprovalService, Celery tasks, OCR signals.
# =============================================================================
from django.utils import timezone
from apps.notifications.models import Notification


class NotificationService:
    @staticmethod
    def create(
        user,
        kind:       str,
        title:      str,
        body:       str = '',
        action_url: str = '',
        expires_at        = None,
    ) -> Notification:
        return Notification.objects.create(
            user=user,
            kind=kind,
            title=title,
            body=body,
            action_url=action_url,
            expires_at=expires_at,
        )

    @staticmethod
    def mark_read(notification_id: int, user) -> bool:
        """Mark a single notification read. Returns True if it existed."""
        updated = Notification.objects.filter(
            pk=notification_id, user=user
        ).update(is_read=True)
        return bool(updated)

    @staticmethod
    def mark_all_read(user) -> int:
        """Mark all unread notifications for `user` as read."""
        return Notification.objects.filter(
            user=user, is_read=False
        ).update(is_read=True)

    @staticmethod
    def unread_count(user) -> int:
        return Notification.objects.filter(user=user, is_read=False).count()

    @staticmethod
    def purge_expired() -> int:
        """Delete notifications whose expires_at is in the past (Celery beat task)."""
        deleted, _ = Notification.objects.filter(
            expires_at__lt=timezone.now()
        ).delete()
        return deleted

    @staticmethod
    def purge_old_read(days: int = 30) -> int:
        """Delete read notifications older than `days` (Celery beat task)."""
        from django.utils.timezone import now
        from datetime import timedelta
        cutoff = now() - timedelta(days=days)
        deleted, _ = Notification.objects.filter(
            is_read=True, created_at__lt=cutoff
        ).delete()
        return deleted

# =============================================================================
# FILE: apps/sharelinks/models.py
# SPRINT 7 — Shareable (public-access) document links
#
# Design decisions:
#   - token: 32-byte URL-safe random string (cryptographically secure)
#   - No authentication required to access a valid, non-expired link
#   - Access is read-only (view/download primary file only)
#   - rate_limit_per_hour: simple sliding-window counter stored in DB
#     (avoids Redis dependency for LAN deployments)
#   - Expiry enforced at view layer + checked on every access
#   - access_log: JSONB list of {ip, ua, accessed_at} — last 100 entries kept
# =============================================================================
import secrets
from django.db import models
from django.conf import settings
from django.utils import timezone


def _default_token():
    return secrets.token_urlsafe(32)


def _default_expiry():
    from datetime import timedelta
    return timezone.now() + timedelta(days=7)


class ShareLink(models.Model):
    class AccessLevel(models.TextChoices):
        VIEW_METADATA = 'VIEW_METADATA', 'View metadata only'
        VIEW_FILE     = 'VIEW_FILE',     'View + download primary file'

    token           = models.CharField(
        max_length=64, unique=True, default=_default_token, db_index=True
    )
    document        = models.ForeignKey(
        'edms.Document', on_delete=models.CASCADE, related_name='share_links'
    )
    revision        = models.ForeignKey(
        'edms.Revision', null=True, blank=True,
        on_delete=models.SET_NULL, related_name='share_links',
        help_text='Pin to a specific revision; null = always latest CURRENT'
    )
    access_level    = models.CharField(
        max_length=20, choices=AccessLevel.choices,
        default=AccessLevel.VIEW_FILE
    )
    label           = models.CharField(
        max_length=200, blank=True,
        help_text='Human-readable purpose, e.g. "Shared with RDSO for review"'
    )
    password_hash   = models.CharField(
        max_length=128, blank=True,
        help_text='bcrypt hash of optional link password. Empty = no password.'
    )
    expires_at      = models.DateTimeField(default=_default_expiry)
    is_active       = models.BooleanField(default=True)
    max_uses        = models.IntegerField(
        null=True, blank=True,
        help_text='Maximum number of accesses. Null = unlimited.'
    )
    use_count       = models.IntegerField(default=0)
    rate_limit_per_hour = models.IntegerField(
        default=20,
        help_text='Max accesses per IP per rolling hour window.'
    )
    access_log      = models.JSONField(
        default=list,
        help_text='Last 100 access events [{ip, ua, accessed_at}]'
    )
    created_by      = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='share_links_created'
    )
    created_at      = models.DateTimeField(auto_now_add=True)
    revoked_by      = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='share_links_revoked'
    )
    revoked_at      = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'sharelink'
        ordering = ['-created_at']

    def __str__(self):
        return f'ShareLink {self.token[:12]}… → {self.document.document_number}'

    @property
    def is_valid(self) -> bool:
        """True if link is active, not expired, and within max_uses."""
        if not self.is_active:
            return False
        if timezone.now() > self.expires_at:
            return False
        if self.max_uses is not None and self.use_count >= self.max_uses:
            return False
        return True

    def record_access(self, ip: str, user_agent: str):
        """Append to access_log (cap at 100), increment use_count."""
        entry = {
            'ip':          ip,
            'ua':          (user_agent or '')[:200],
            'accessed_at': timezone.now().isoformat(),
        }
        log = list(self.access_log)   # copy
        log.append(entry)
        self.access_log = log[-100:]  # keep last 100
        self.use_count += 1
        self.save(update_fields=['access_log', 'use_count'])

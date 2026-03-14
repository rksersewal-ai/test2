# =============================================================================
# FILE: apps/sharelinks/services.py
# SPRINT 7 — ShareLink business logic
# =============================================================================
import hashlib
from datetime import timedelta
from typing   import Optional

from django.utils import timezone
from django.db    import transaction

from apps.sharelinks.models import ShareLink
from apps.audit.services    import AuditService


class ShareLinkService:

    @staticmethod
    @transaction.atomic
    def create(
        document,
        created_by,
        revision         = None,
        access_level     = ShareLink.AccessLevel.VIEW_FILE,
        label            = '',
        expires_in_days  = 7,
        max_uses         = None,
        rate_limit       = 20,
        password: Optional[str] = None,
    ) -> ShareLink:
        expires_at = timezone.now() + timedelta(days=expires_in_days)
        pw_hash    = ''
        if password:
            import bcrypt
            pw_hash = bcrypt.hashpw(
                password.encode(), bcrypt.gensalt()
            ).decode()

        link = ShareLink.objects.create(
            document             = document,
            revision             = revision,
            access_level         = access_level,
            label                = label,
            expires_at           = expires_at,
            max_uses             = max_uses,
            rate_limit_per_hour  = rate_limit,
            password_hash        = pw_hash,
            created_by           = created_by,
        )
        AuditService.log(
            user             = created_by,
            module           = 'SHARELINKS',
            action           = 'CREATE_SHARE_LINK',
            entity_type      = 'ShareLink',
            entity_id        = link.pk,
            entity_identifier = link.token[:12] + '…',
            description      = (
                f'Share link created for {document.document_number}. '
                f'Expires: {expires_at.date()}. '
                f'Level: {access_level}.'
            ),
        )
        return link

    @staticmethod
    def revoke(link: ShareLink, revoked_by) -> ShareLink:
        link.is_active  = False
        link.revoked_by = revoked_by
        link.revoked_at = timezone.now()
        link.save(update_fields=['is_active', 'revoked_by', 'revoked_at'])
        AuditService.log(
            user             = revoked_by,
            module           = 'SHARELINKS',
            action           = 'REVOKE_SHARE_LINK',
            entity_type      = 'ShareLink',
            entity_id        = link.pk,
            entity_identifier = link.token[:12] + '…',
            description      = f'Share link revoked for {link.document.document_number}.',
        )
        return link

    @staticmethod
    def check_rate_limit(link: ShareLink, ip: str) -> bool:
        """
        Return True if the IP is within rate_limit_per_hour for this link.
        Uses access_log for a simple sliding-window count — no Redis needed.
        """
        window_start = (timezone.now() - timedelta(hours=1)).isoformat()
        recent = [
            e for e in link.access_log
            if e.get('ip') == ip and e.get('accessed_at', '') >= window_start
        ]
        return len(recent) < link.rate_limit_per_hour

    @staticmethod
    def verify_password(link: ShareLink, password: str) -> bool:
        if not link.password_hash:
            return True   # no password set
        try:
            import bcrypt
            return bcrypt.checkpw(password.encode(), link.password_hash.encode())
        except Exception:
            return False

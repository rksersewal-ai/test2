"""AuditService — single entry point for all audit log writes.

All modules (EDMS, workflow, OCR, auth) call AuditService.log().
The request object is optional; pass it in middleware-aware contexts
to capture IP and user-agent automatically.
"""
import logging
from apps.audit.models import AuditLog

logger = logging.getLogger(__name__)


class AuditService:
    @staticmethod
    def log(
        *,
        user=None,
        module: str,
        action: str,
        entity_type: str = '',
        entity_id: int | None = None,
        entity_identifier: str = '',
        description: str = '',
        extra_data: dict | None = None,
        ip_address: str | None = None,
        user_agent: str = '',
        success: bool = True,
        request=None,          # optional Django request for IP/UA extraction
    ) -> AuditLog | None:
        """Create one immutable audit log entry. Never raises — failures are logged."""
        try:
            if request is not None:
                ip_address = ip_address or _get_client_ip(request)
                user_agent = user_agent or request.META.get('HTTP_USER_AGENT', '')[:500]
                if user is None:
                    user = getattr(request, 'user', None) or None

            username = ''
            full_name = ''
            if user and user.pk:
                username  = getattr(user, 'username', '') or ''
                full_name = getattr(user, 'get_full_name', lambda: '')() or ''

            entry = AuditLog(
                user=user if (user and user.pk) else None,
                username=username,
                user_full_name=full_name,
                module=module,
                action=action,
                entity_type=entity_type,
                entity_id=entity_id,
                entity_identifier=entity_identifier,
                description=description,
                extra_data=extra_data,
                ip_address=ip_address,
                user_agent=user_agent,
                success=success,
            )
            entry.save()
            return entry
        except Exception as exc:  # noqa: BLE001
            logger.error('AuditService.log failed: %s', exc, exc_info=True)
            return None


def _get_client_ip(request) -> str | None:
    """Extract real client IP — handles X-Forwarded-For from nginx/IIS reverse proxy."""
    xff = request.META.get('HTTP_X_FORWARDED_FOR')
    if xff:
        return xff.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR')

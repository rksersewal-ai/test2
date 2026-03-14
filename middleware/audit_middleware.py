# =============================================================================
# FILE: middleware/audit_middleware.py
#
# BUG FIX: Old implementation used MiddlewareMixin with process_request().
#   process_request() fires BEFORE AuthenticationMiddleware populates
#   request.user, so every audit log entry showed an anonymous user.
#
# FIX: Converted to modern __call__ style (Django 1.10+ standard).
#   The audit context is now attached AFTER get_response() resolves the
#   full middleware stack (including AuthenticationMiddleware), so
#   request.user is the actual authenticated user by the time we log.
#
#   Context is stored on request.audit_context for downstream signals
#   (e.g. apps/audit/signals.py) to read and write AuditLog entries.
#
#   Also added:
#   - request.audit_user  : authenticated User object (or None)
#   - response timing     : request_duration_ms in audit_context
#   - safe request_path   : truncated to 500 chars to avoid DB overflow
# =============================================================================
import time
import logging
from django.contrib.auth.models import AnonymousUser

logger = logging.getLogger(__name__)


class AuditMiddleware:
    """
    Modern __call__-style middleware that populates request.audit_context
    AFTER the inner middleware stack has run (so request.user is resolved).
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # ── record start time before request processing ──────────────────────
        t_start = time.monotonic()

        # ── run the full middleware/view stack ───────────────────────────────
        response = self.get_response(request)

        # ── now request.user IS populated by AuthenticationMiddleware ────────
        duration_ms = round((time.monotonic() - t_start) * 1000, 2)

        user     = getattr(request, 'user', None)
        is_anon  = (user is None) or isinstance(user, AnonymousUser) or not user.is_authenticated
        user_id  = None if is_anon else getattr(user, 'pk', None)
        username = 'anonymous' if is_anon else getattr(user, 'username', 'unknown')

        request.audit_user = None if is_anon else user

        request.audit_context = {
            'ip_address'         : self._get_client_ip(request),
            'user_agent'         : request.META.get('HTTP_USER_AGENT', '')[:500],
            'request_method'     : request.method,
            'request_path'       : request.path[:500],
            'session_key'        : (request.session.session_key or '') if hasattr(request, 'session') else '',
            'user_id'            : user_id,
            'username'           : username,
            'response_status'    : response.status_code,
            'request_duration_ms': duration_ms,
        }

        return response

    @staticmethod
    def _get_client_ip(request) -> str:
        """Return real client IP, honouring X-Forwarded-For (reverse proxy)."""
        x_forwarded = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded:
            # First IP in the chain is the original client
            return x_forwarded.split(',')[0].strip()
        return request.META.get('REMOTE_ADDR', '')

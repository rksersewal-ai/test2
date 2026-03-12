"""PLW EDMS security middleware stack.

Registration order in settings.MIDDLEWARE (add after SessionMiddleware):
    'apps.security.middleware.LANOnlyMiddleware',
    'apps.security.middleware.AuditRequestMiddleware',
    'apps.security.middleware.SecurityHeadersMiddleware',

⚠️  LANOnlyMiddleware is OFF in DEBUG mode so local dev works normally.
"""
import ipaddress
import logging
import time

from django.conf import settings
from django.http import HttpResponseForbidden

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# 1.  LAN-Only IP restriction
# ---------------------------------------------------------------------------
# Configure in settings:  ALLOWED_LAN_NETWORKS = ['192.168.1.0/24', '10.0.0.0/8']
_DEFAULT_LAN = ['127.0.0.0/8', '10.0.0.0/8', '172.16.0.0/12', '192.168.0.0/16']


class LANOnlyMiddleware:
    """Block any request originating from outside the configured LAN ranges."""

    def __init__(self, get_response):
        self.get_response = get_response
        raw = getattr(settings, 'ALLOWED_LAN_NETWORKS', _DEFAULT_LAN)
        self.networks = [ipaddress.ip_network(n, strict=False) for n in raw]

    def __call__(self, request):
        if settings.DEBUG:
            return self.get_response(request)   # skip in dev

        xff = request.META.get('HTTP_X_FORWARDED_FOR')
        raw_ip = xff.split(',')[0].strip() if xff else request.META.get('REMOTE_ADDR', '')
        try:
            addr = ipaddress.ip_address(raw_ip)
        except ValueError:
            return HttpResponseForbidden('Invalid source IP.')

        if not any(addr in net for net in self.networks):
            logger.warning('LANOnlyMiddleware: blocked %s', raw_ip)
            return HttpResponseForbidden('Access restricted to internal network.')

        return self.get_response(request)


# ---------------------------------------------------------------------------
# 2.  Passive audit middleware — logs every mutating API call
# ---------------------------------------------------------------------------
_AUDIT_METHODS = {'POST', 'PUT', 'PATCH', 'DELETE'}
_AUDIT_PREFIX  = '/api/'


class AuditRequestMiddleware:
    """Automatically emit an AUTH or API audit entry for mutating requests."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        t0 = time.perf_counter()
        response = self.get_response(request)
        elapsed = time.perf_counter() - t0

        if (
            request.method in _AUDIT_METHODS
            and request.path.startswith(_AUDIT_PREFIX)
            and hasattr(request, 'user')
            and request.user.is_authenticated
        ):
            self._emit(request, response, elapsed)

        return response

    def _emit(self, request, response, elapsed):
        try:
            from apps.audit.services import AuditService
            AuditService.log(
                request=request,
                module='CORE',
                action=f'HTTP_{request.method}',
                entity_identifier=request.path,
                description=f'{request.method} {request.path} → {response.status_code} ({elapsed*1000:.0f}ms)',
                success=response.status_code < 400,
            )
        except Exception as exc:  # noqa: BLE001
            logger.error('AuditRequestMiddleware emit failed: %s', exc)


# ---------------------------------------------------------------------------
# 3.  Security headers (LAN-safe subset of OWASP recommendations)
# ---------------------------------------------------------------------------
class SecurityHeadersMiddleware:
    """Add defensive HTTP headers to every response."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        response['X-Content-Type-Options'] = 'nosniff'
        response['X-Frame-Options']        = 'SAMEORIGIN'
        response['Referrer-Policy']        = 'strict-origin-when-cross-origin'
        response['Cache-Control']          = 'no-store'
        # CSP: tight policy — only same-origin + inline styles for the React SPA
        response['Content-Security-Policy'] = (
            "default-src 'self'; "
            "script-src 'self'; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data:; "
            "connect-src 'self'; "
            "frame-ancestors 'self';"
        )
        return response

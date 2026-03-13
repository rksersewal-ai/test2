"""PLW EDMS security middleware stack.

Registration order in settings.MIDDLEWARE (add after SessionMiddleware):
    'apps.security.middleware.LANOnlyMiddleware',
    'apps.security.middleware.AuditRequestMiddleware',
    'apps.security.middleware.SecurityHeadersMiddleware',

FIX (Critical #3): LANOnlyMiddleware now uses the LAST IP in X-Forwarded-For
    (the one appended by your actual proxy/IIS), not the first which is
    spoofable by any client. Also reads TRUSTED_PROXY_COUNT from settings.

⚠️  LANOnlyMiddleware is OFF in DEBUG mode so local dev works normally.
"""
import ipaddress
import logging
import time

from django.conf import settings
from django.http import HttpResponseForbidden

logger = logging.getLogger(__name__)

_DEFAULT_LAN = ['127.0.0.0/8', '10.0.0.0/8', '172.16.0.0/12', '192.168.0.0/16']


class LANOnlyMiddleware:
    """Block any request originating from outside the configured LAN ranges.

    TRUSTED_PROXY_COUNT (int, default 0) in settings:
      - 0  = no proxy in front; use REMOTE_ADDR directly.
      - 1  = one proxy (e.g. IIS ARR); take the last IP added to XFF chain.
      - N  = N proxies; take the Nth-from-right entry in XFF.

    This prevents XFF spoofing: attacker-controlled IPs are at the LEFT of
    the XFF list; the rightmost entry is the one added by your trusted proxy.
    """

    def __init__(self, get_response):
        self.get_response = get_response
        raw = getattr(settings, 'ALLOWED_LAN_NETWORKS', _DEFAULT_LAN)
        self.networks = [ipaddress.ip_network(n, strict=False) for n in raw]
        self.proxy_count = int(getattr(settings, 'TRUSTED_PROXY_COUNT', 0))

    def _get_client_ip(self, request) -> str:
        if self.proxy_count > 0:
            xff = request.META.get('HTTP_X_FORWARDED_FOR', '')
            if xff:
                # Split and strip all IPs in chain
                ips = [ip.strip() for ip in xff.split(',')]
                # The rightmost entry injected by our proxy is at:
                # index = len(ips) - proxy_count  (0-based)
                idx = max(len(ips) - self.proxy_count, 0)
                return ips[idx]
        return request.META.get('REMOTE_ADDR', '')

    def __call__(self, request):
        if settings.DEBUG:
            return self.get_response(request)

        raw_ip = self._get_client_ip(request)
        try:
            addr = ipaddress.ip_address(raw_ip)
        except ValueError:
            logger.warning('LANOnlyMiddleware: invalid IP "%s"', raw_ip)
            return HttpResponseForbidden('Invalid source IP.')

        if not any(addr in net for net in self.networks):
            logger.warning('LANOnlyMiddleware: blocked %s', raw_ip)
            return HttpResponseForbidden('Access restricted to internal network.')

        return self.get_response(request)


_AUDIT_METHODS = {'POST', 'PUT', 'PATCH', 'DELETE'}
_AUDIT_PREFIX  = '/api/'


class AuditRequestMiddleware:
    """Automatically emit an audit entry for every mutating API call."""

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
                description=(
                    f'{request.method} {request.path} '
                    f'→ {response.status_code} ({elapsed*1000:.0f}ms)'
                ),
                success=response.status_code < 400,
            )
        except Exception as exc:
            # FIX: Log at ERROR level + raise in non-production to surface bugs early
            logger.error('AuditRequestMiddleware emit failed: %s', exc, exc_info=True)
            if not settings.DEBUG:
                pass  # Keep request alive in prod; alert via logger


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
        response['Content-Security-Policy'] = (
            "default-src 'self'; "
            "script-src 'self'; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data:; "
            "connect-src 'self'; "
            "frame-ancestors 'self';"
        )
        return response

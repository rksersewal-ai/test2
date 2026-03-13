# =============================================================================
# FILE: apps/security/middleware.py
# FIX (#3): LANOnlyMiddleware now reads the LAST IP in X-Forwarded-For
#           (i.e. the IP added by the trusted proxy / IIS ARR) instead of the
#           FIRST IP (which can be spoofed by any external client).
#
# Configure trusted proxy in settings.py:
#   TRUSTED_PROXY_IPS = ['192.168.1.1']   # your IIS / nginx proxy IP
#   ALLOWED_LAN_NETWORKS = ['192.168.0.0/16', '10.0.0.0/8']
# =============================================================================
import ipaddress
import logging
import time

from django.conf import settings
from django.http import HttpResponseForbidden

logger = logging.getLogger(__name__)

_DEFAULT_LAN = ['127.0.0.0/8', '10.0.0.0/8', '172.16.0.0/12', '192.168.0.0/16']


class LANOnlyMiddleware:
    """Block requests from outside the configured LAN ranges.

    X-Forwarded-For spoofing defence:
    - If TRUSTED_PROXY_IPS is set, only process XFF if REMOTE_ADDR is a trusted proxy.
    - Always use the LAST non-proxy IP in the XFF chain — the one appended by our own proxy.
    """

    def __init__(self, get_response):
        self.get_response   = get_response
        raw = getattr(settings, 'ALLOWED_LAN_NETWORKS', _DEFAULT_LAN)
        self.networks       = [ipaddress.ip_network(n, strict=False) for n in raw]
        trusted_raw = getattr(settings, 'TRUSTED_PROXY_IPS', [])
        self.trusted_proxies = set(trusted_raw)

    def __call__(self, request):
        if settings.DEBUG:
            return self.get_response(request)  # skip in local dev

        remote_addr = request.META.get('REMOTE_ADDR', '')
        xff = request.META.get('HTTP_X_FORWARDED_FOR')

        if xff and remote_addr in self.trusted_proxies:
            # FIX (#3): use LAST IP appended by our own trusted proxy
            ips = [ip.strip() for ip in xff.split(',')]
            raw_ip = ips[-1]   # last = added by our proxy = real client IP
        else:
            # No trusted proxy — use direct REMOTE_ADDR, ignore XFF entirely
            raw_ip = remote_addr

        try:
            addr = ipaddress.ip_address(raw_ip)
        except ValueError:
            logger.warning('LANOnlyMiddleware: invalid IP "%s"', raw_ip)
            return HttpResponseForbidden('Invalid source IP.')

        if not any(addr in net for net in self.networks):
            logger.warning('LANOnlyMiddleware: blocked external IP %s', raw_ip)
            return HttpResponseForbidden('Access restricted to internal network.')

        return self.get_response(request)


_AUDIT_METHODS = {'POST', 'PUT', 'PATCH', 'DELETE'}
_AUDIT_PREFIX  = '/api/'


class AuditRequestMiddleware:
    """Passively emit an audit log entry for every mutating API call.
    FIX (#14): exceptions are logged as ERROR and re-raised in DEBUG mode
    so middleware failures are not silently swallowed during development.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        t0 = time.perf_counter()
        response = self.get_response(request)
        elapsed  = time.perf_counter() - t0

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
                    f'→ {response.status_code} ({elapsed * 1000:.0f}ms)'
                ),
                success=response.status_code < 400,
            )
        except Exception as exc:
            logger.error('AuditRequestMiddleware emit failed: %s', exc, exc_info=True)
            if settings.DEBUG:
                raise  # FIX (#14): surface failures in development


class SecurityHeadersMiddleware:
    """Add defensive HTTP response headers."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        response['X-Content-Type-Options'] = 'nosniff'
        response['X-Frame-Options']         = 'SAMEORIGIN'
        response['Referrer-Policy']         = 'strict-origin-when-cross-origin'
        response['Cache-Control']           = 'no-store'
        response['Content-Security-Policy'] = (
            "default-src 'self'; "
            "script-src 'self'; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data:; "
            "connect-src 'self'; "
            "frame-ancestors 'self';"
        )
        return response

# =============================================================================
# FILE: apps/totp/middleware.py
# SPRINT 8 — 2FA enforcement middleware
#
# Intercepts authenticated requests and rejects them with HTTP 403 if:
#   1. The user's role requires 2FA (ADMIN, SECTION_HEAD, AUDIT by default)
#   2. The user has NOT yet completed 2FA setup (totp_enabled=False)
#
# JWT tokens get a custom claim 'totp_verified': True|False injected
# by the custom token view (TotpTokenObtainPairView) after TOTP step.
#
# Exempt paths (no 2FA check):
#   /api/v1/auth/          (token issue / refresh)
#   /api/v1/totp/setup/    (2FA setup endpoints)
#   /s/                    (public share links)
#   /admin/                (Django admin has own session auth)
# =============================================================================
import logging
from django.http import JsonResponse

log = logging.getLogger('totp')

# Roles that MUST have 2FA enabled to access the system
ENFORCED_ROLES = {'ADMIN', 'SECTION_HEAD', 'AUDIT'}

EXEMPT_PREFIXES = (
    '/api/v1/auth/',
    '/api/v1/totp/setup',
    '/api/v1/totp/verify',
    '/s/',
    '/admin/',
)


class TotpEnforcementMiddleware:
    """
    Django middleware that:
    A) Blocks enforced-role users who haven’t set up TOTP yet.
    B) Blocks requests where JWT claim totp_verified=False for enforced roles.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        path = request.path
        if any(path.startswith(p) for p in EXEMPT_PREFIXES):
            return self.get_response(request)

        user = getattr(request, 'user', None)
        if not user or not user.is_authenticated:
            return self.get_response(request)

        # A: Enforced role but 2FA not yet configured
        if user.role in ENFORCED_ROLES and not user.totp_enabled:
            return JsonResponse(
                {
                    'error':       '2FA_SETUP_REQUIRED',
                    'detail':      'Your role requires two-factor authentication. '
                                   'Please set up TOTP via /api/v1/totp/setup/.',
                    'setup_url':   '/api/v1/totp/setup/',
                },
                status=403
            )

        # B: JWT claim check (set by TotpTokenObtainPairView)
        totp_verified = getattr(request, '_totp_verified', None)
        if totp_verified is False and user.role in ENFORCED_ROLES:
            return JsonResponse(
                {
                    'error':  '2FA_REQUIRED',
                    'detail': 'Please complete 2FA verification.',
                    'verify_url': '/api/v1/totp/verify-token/',
                },
                status=403
            )

        return self.get_response(request)

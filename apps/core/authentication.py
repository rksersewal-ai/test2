# =============================================================================
# FILE: apps/core/authentication.py
# BUG FIX #8: Invalid/tampered JWT cookies were silently swallowed with bare
#   `pass`, producing zero audit trail. For a Railways compliance system this
#   is unacceptable — every tampered-token attempt must appear in logs.
#   Added WARNING log with client IP so audit middleware can correlate it.
# =============================================================================
import logging

from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError

logger = logging.getLogger(__name__)


class JWTCookieAuthentication(JWTAuthentication):
    """Read JWT access token from the httpOnly cookie first, fallback to Authorization header."""

    def authenticate(self, request):
        raw_token = request.COOKIES.get('access_token')
        if raw_token:
            try:
                validated_token = self.get_validated_token(raw_token)
                return self.get_user(validated_token), validated_token
            except (InvalidToken, TokenError) as exc:
                # BUG FIX #8: log invalid cookie token — visible in audit trail
                client_ip = (
                    request.META.get('HTTP_X_FORWARDED_FOR', '').split(',')[0].strip()
                    or request.META.get('REMOTE_ADDR', 'unknown')
                )
                logger.warning(
                    'Invalid/expired JWT cookie from %s: %s',
                    client_ip,
                    exc,
                )
                # Do NOT return immediately — fall through to header auth
                # so API clients using Bearer token still work.

        header = self.get_header(request)
        if header is None:
            return None

        raw_token = self.get_raw_token(header)
        if raw_token is None:
            return None

        validated_token = self.get_validated_token(raw_token)
        return self.get_user(validated_token), validated_token

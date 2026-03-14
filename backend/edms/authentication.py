# =============================================================================
# FILE: backend/edms/authentication.py
# Cookie-based JWT authentication backend.
# Reads 'access_token' from httpOnly cookie instead of Authorization header.
# Register in settings.py REST_FRAMEWORK DEFAULT_AUTHENTICATION_CLASSES.
# =============================================================================
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError


class JWTCookieAuthentication(JWTAuthentication):
    """
    Authenticate using the 'access_token' httpOnly cookie.
    Falls back to Authorization: Bearer header if cookie is absent
    (allows DRF Browsable API + curl to still work).
    """

    def authenticate(self, request):
        # 1. Try cookie first
        raw_token = request.COOKIES.get('access_token')
        if raw_token:
            try:
                validated = self.get_validated_token(raw_token)
                return self.get_user(validated), validated
            except (InvalidToken, TokenError):
                pass  # fall through to header

        # 2. Fall back to Authorization header (Bearer)
        header = self.get_header(request)
        if header is None:
            return None
        raw_token = self.get_raw_token(header)
        if raw_token is None:
            return None
        validated = self.get_validated_token(raw_token)
        return self.get_user(validated), validated

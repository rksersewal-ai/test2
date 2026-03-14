# =============================================================================
# FILE: apps/totp/views.py
# SPRINT 8 — TOTP / 2FA REST API
#
# POST /api/v1/totp/setup/             — Step 1: generate secret, return QR
# POST /api/v1/totp/setup/confirm/     — Step 2: verify first code, enable 2FA
# POST /api/v1/totp/verify-token/      — Exchange partial JWT + TOTP code
#                                         for full JWT with totp_verified=True
# POST /api/v1/totp/disable/           — Disable 2FA (requires current code)
# GET  /api/v1/totp/status/            — 2FA status for current user
# POST /api/v1/totp/backup-codes/regen/— Regenerate backup codes
# POST /api/v1/auth/token/2fa/         — Full login (password + TOTP in one step)
# =============================================================================
import logging
from django.utils import timezone
from rest_framework import permissions, status
from rest_framework.views    import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from apps.totp.engine import generate_secret, verify_code, qr_png_data_uri
from apps.totp.serializers import (
    TotpConfirmSerializer, TotpVerifySerializer,
    TotpDisableSerializer, TotpLoginSerializer,
)

log = logging.getLogger('totp')


class TotpSetupView(APIView):
    """
    POST /api/v1/totp/setup/
    Generates a new TOTP secret for the user (does NOT enable 2FA yet).
    Returns QR code PNG data URI + plaintext secret for manual entry.
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        user = request.user
        if user.totp_enabled:
            return Response(
                {'error': '2FA is already enabled. Disable it first to re-enroll.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        secret = generate_secret()
        # Save as pending (not yet enabled)
        user.totp_secret = secret
        user.save(update_fields=['totp_secret'])

        return Response({
            'secret':   secret,
            'qr_uri':   qr_png_data_uri(secret, user.username),
            'message':  'Scan QR code with your authenticator app, then POST a '
                        'valid code to /api/v1/totp/setup/confirm/ to activate.',
        })


class TotpSetupConfirmView(APIView):
    """
    POST /api/v1/totp/setup/confirm/  {code: '123456'}
    Verifies the first TOTP code, marks totp_enabled=True, returns backup codes.
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        user = request.user
        ser  = TotpConfirmSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        code = ser.validated_data['code']

        if not user.totp_secret:
            return Response(
                {'error': 'No TOTP secret found. Call /api/v1/totp/setup/ first.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        if not verify_code(user.totp_secret, code):
            return Response(
                {'error': 'Invalid TOTP code. Check your authenticator app.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        user.totp_enabled    = True
        user.totp_enforced_at = timezone.now()
        user.save(update_fields=['totp_enabled', 'totp_enforced_at'])

        plaintext_codes = user.generate_backup_codes()
        log.info(f'[TOTP] 2FA enabled for user={user.username}')

        return Response({
            'status':       '2FA enabled',
            'backup_codes': plaintext_codes,
            'warning':      'Save these backup codes now. They will NOT be shown again.',
        })


class TotpVerifyTokenView(APIView):
    """
    POST /api/v1/totp/verify-token/
    Body: {refresh_token, code}
    After password login, the user receives a 'partial' JWT (totp_verified=False).
    This endpoint validates the TOTP code and returns a full JWT.
    """
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        ser = TotpVerifySerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        d = ser.validated_data

        # Decode the partial refresh token to get the user
        from rest_framework_simplejwt.tokens import RefreshToken, TokenError
        try:
            token = RefreshToken(d['refresh_token'])
            user_id = token.payload.get('user_id')
        except TokenError:
            return Response({'error': 'Invalid or expired token.'}, status=400)

        from django.contrib.auth import get_user_model
        User = get_user_model()
        try:
            user = User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return Response({'error': 'User not found.'}, status=404)

        code        = d['code']
        is_backup   = len(code.replace('-', '').replace(' ', '')) > 6

        if is_backup:
            if not user.consume_backup_code(code):
                return Response({'error': 'Invalid backup code.'}, status=400)
        else:
            if not verify_code(user.totp_secret, code):
                return Response({'error': 'Invalid TOTP code.'}, status=400)

        # Issue full JWT with totp_verified=True
        refresh = _make_full_token(user)
        log.info(f'[TOTP] 2FA verified for user={user.username}')
        return Response({
            'refresh': str(refresh),
            'access':  str(refresh.access_token),
        })


class TotpLoginView(APIView):
    """
    POST /api/v1/auth/token/2fa/  {username, password, code}
    All-in-one login endpoint: validates password + TOTP in one request.
    Useful for CLI tools, API integrations, PWA scanner.
    """
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        ser = TotpLoginSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        d = ser.validated_data

        from django.contrib.auth import authenticate
        user = authenticate(request, username=d['username'], password=d['password'])
        if not user:
            return Response({'error': 'Invalid credentials.'}, status=401)
        if not user.is_active:
            return Response({'error': 'Account disabled.'}, status=403)

        if user.totp_enabled:
            code = d.get('code', '')
            if not code:
                # Return partial token: totp_verified=False
                refresh = _make_partial_token(user)
                return Response({
                    'totp_required': True,
                    'refresh':       str(refresh),
                    'access':        str(refresh.access_token),
                    'verify_url':    '/api/v1/totp/verify-token/',
                }, status=200)

            if not verify_code(user.totp_secret, code):
                if not user.consume_backup_code(code):
                    return Response({'error': 'Invalid TOTP/backup code.'}, status=400)

        refresh = _make_full_token(user)
        return Response({
            'refresh':       str(refresh),
            'access':        str(refresh.access_token),
            'totp_required': False,
        })


class TotpDisableView(APIView):
    """POST /api/v1/totp/disable/ {code}  — disable 2FA (requires valid code)."""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        ser = TotpDisableSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        user = request.user
        code = ser.validated_data['code']

        if not user.totp_enabled:
            return Response({'error': '2FA is not enabled.'}, status=400)
        if not verify_code(user.totp_secret, code):
            return Response({'error': 'Invalid code. Provide current TOTP to disable.'}, status=400)

        user.totp_enabled    = False
        user.totp_secret     = ''
        user.totp_backup_codes = []
        user.totp_enforced_at  = None
        user.save(update_fields=[
            'totp_enabled', 'totp_secret', 'totp_backup_codes', 'totp_enforced_at'
        ])
        log.info(f'[TOTP] 2FA disabled for user={user.username}')
        return Response({'status': '2FA disabled successfully.'})


class TotpStatusView(APIView):
    """GET /api/v1/totp/status/  — current user 2FA status."""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        return Response({
            'totp_enabled':       user.totp_enabled,
            'backup_codes_count': len(user.totp_backup_codes),
            'enforced_for_role':  user.role in {'ADMIN', 'SECTION_HEAD', 'AUDIT'},
            'setup_url':          '/api/v1/totp/setup/' if not user.totp_enabled else None,
        })


class TotpRegenBackupCodesView(APIView):
    """POST /api/v1/totp/backup-codes/regen/ {code}  — regenerate backup codes."""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        user = request.user
        ser  = TotpDisableSerializer(data=request.data)  # reuse {code} shape
        ser.is_valid(raise_exception=True)
        if not user.totp_enabled:
            return Response({'error': '2FA not enabled.'}, status=400)
        if not verify_code(user.totp_secret, ser.validated_data['code']):
            return Response({'error': 'Invalid TOTP code.'}, status=400)

        plaintext_codes = user.generate_backup_codes()
        return Response({
            'backup_codes': plaintext_codes,
            'warning':      'Save these backup codes now. Previous codes are now invalid.',
        })


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_full_token(user):
    """Issue a JWT with totp_verified=True in the payload."""
    refresh = RefreshToken.for_user(user)
    refresh['totp_verified'] = True
    refresh['role']          = user.role
    return refresh


def _make_partial_token(user):
    """Issue a JWT with totp_verified=False (pre-2FA login)."""
    refresh = RefreshToken.for_user(user)
    refresh['totp_verified'] = False
    refresh['role']          = user.role
    return refresh

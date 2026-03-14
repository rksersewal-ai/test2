# =============================================================================
# FILE: apps/totp/serializers.py
# SPRINT 8
# =============================================================================
from rest_framework import serializers


class TotpConfirmSerializer(serializers.Serializer):
    code = serializers.CharField(min_length=6, max_length=8,
                                  help_text='6-digit TOTP code from authenticator app.')


class TotpVerifySerializer(serializers.Serializer):
    refresh_token = serializers.CharField()
    code          = serializers.CharField(min_length=6, max_length=20,
                                           help_text='6-digit TOTP code OR backup code.')


class TotpDisableSerializer(serializers.Serializer):
    code = serializers.CharField(min_length=6, max_length=8)


class TotpLoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)
    code     = serializers.CharField(
        required=False, allow_blank=True,
        help_text='TOTP code. Omit to get partial token for two-step flow.'
    )

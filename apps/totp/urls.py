# =============================================================================
# FILE: apps/totp/urls.py
# SPRINT 8
# =============================================================================
from django.urls import path
from apps.totp.views import (
    TotpSetupView, TotpSetupConfirmView, TotpVerifyTokenView,
    TotpDisableView, TotpStatusView, TotpRegenBackupCodesView,
    TotpLoginView,
)

urlpatterns = [
    path('setup/',               TotpSetupView.as_view(),           name='totp-setup'),
    path('setup/confirm/',       TotpSetupConfirmView.as_view(),    name='totp-setup-confirm'),
    path('verify-token/',        TotpVerifyTokenView.as_view(),     name='totp-verify-token'),
    path('disable/',             TotpDisableView.as_view(),         name='totp-disable'),
    path('status/',              TotpStatusView.as_view(),          name='totp-status'),
    path('backup-codes/regen/',  TotpRegenBackupCodesView.as_view(), name='totp-backup-regen'),
    # Combined login
    path('login/',               TotpLoginView.as_view(),           name='totp-login'),
]

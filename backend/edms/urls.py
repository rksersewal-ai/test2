# =============================================================================
# FILE: backend/edms/urls.py  — EDMS main URL configuration
# UPDATED: Added pl-master/ prefix including all PL-related routes
# PORT POLICY: Backend 8765, Frontend 4173
# =============================================================================
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from .auth import (
    EDMSTokenObtainPairView,
    EDMSTokenRefreshView,
    EDMSLogoutView,
    EDMSMeView,
)
from rest_framework_simplejwt.views import TokenVerifyView

urlpatterns = [
    path('admin/', admin.site.urls),

    # ── Auth ───────────────────────────────────────────────────────────────────
    path('api/v1/auth/token/',         EDMSTokenObtainPairView.as_view(), name='token_obtain'),
    path('api/v1/auth/token/refresh/', EDMSTokenRefreshView.as_view(),    name='token_refresh'),
    path('api/v1/auth/token/verify/',  TokenVerifyView.as_view(),         name='token_verify'),
    path('api/v1/auth/logout/',        EDMSLogoutView.as_view(),          name='logout'),
    path('api/v1/auth/me/',            EDMSMeView.as_view(),              name='auth_me'),

    # ── Master data (loco types, components, lookups) ────────────────────────────
    path('api/v1/master/',    include('master.urls')),

    # ── PL Master (PLItems, VendorInfo, TechEvalDocs, LinkedDocs) ───────────────
    path('api/v1/pl-master/', include('master.urls_pl_master')),

    # ── Other EDMS modules ──────────────────────────────────────────────────────
    path('api/v1/config/',    include('config_mgmt.urls')),
    path('api/v1/prototype/', include('prototype.urls')),
    path('api/v1/ocr/',       include('ocr_queue.urls')),
    path('api/v1/audit/',     include('audit_log.urls')),
]

# Serve uploaded media files in development (and on LAN without a reverse proxy)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
else:
    # In production/staging, also serve media via Django if no nginx configured
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

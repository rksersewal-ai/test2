# =============================================================================
# FILE: backend/edms/urls.py  — EDMS main URL configuration
# BUG FIX: Added /auth/me/ endpoint (used by AuthContext session-verify on mount)
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

    # ---- Auth ---------------------------------------------------------------
    path('api/v1/auth/token/',         EDMSTokenObtainPairView.as_view(), name='token_obtain'),
    path('api/v1/auth/token/refresh/', EDMSTokenRefreshView.as_view(),    name='token_refresh'),
    path('api/v1/auth/token/verify/',  TokenVerifyView.as_view(),         name='token_verify'),
    path('api/v1/auth/logout/',        EDMSLogoutView.as_view(),          name='logout'),
    path('api/v1/auth/me/',            EDMSMeView.as_view(),              name='auth_me'),

    # ---- EDMS modules -------------------------------------------------------
    path('api/v1/master/',    include('master.urls')),
    path('api/v1/config/',    include('config_mgmt.urls')),
    path('api/v1/prototype/', include('prototype.urls')),
    path('api/v1/ocr/',       include('ocr_queue.urls')),
    path('api/v1/audit/',     include('audit_log.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

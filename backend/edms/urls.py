# =============================================================================
# FILE: backend/edms/urls.py  — EDMS main URL configuration
# All API routes versioned under /api/v1/
# =============================================================================
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework_simplejwt.views import (
    TokenObtainPairView, TokenRefreshView, TokenVerifyView,
)

urlpatterns = [
    # Django Admin
    path('admin/', admin.site.urls),

    # ---- Authentication (JWT) -----------------------------------------------
    path('api/v1/auth/token/',         TokenObtainPairView.as_view(),  name='token_obtain'),
    path('api/v1/auth/token/refresh/', TokenRefreshView.as_view(),     name='token_refresh'),
    path('api/v1/auth/token/verify/',  TokenVerifyView.as_view(),      name='token_verify'),

    # ---- Master Data ----------------------------------------------------------
    path('api/v1/master/',   include('master.urls')),

    # ---- Configuration Management -------------------------------------------
    path('api/v1/config/',   include('config_mgmt.urls')),

    # ---- Prototype Inspection ------------------------------------------------
    path('api/v1/prototype/', include('prototype.urls')),

    # ---- OCR Queue -----------------------------------------------------------
    path('api/v1/ocr/',      include('ocr_queue.urls')),

    # ---- Audit Log -----------------------------------------------------------
    path('api/v1/audit/',    include('audit_log.urls')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

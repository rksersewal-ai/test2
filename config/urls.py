# =============================================================================
# FILE: config/urls.py
# SPRINT 8 UPDATE (FINAL): Added TOTP + scanner routes.
# All previous routes preserved exactly.
# =============================================================================
from django.contrib import admin
from django.urls    import path, include
from django.conf    import settings
from django.conf.urls.static import static
from rest_framework_simplejwt.views import (
    TokenObtainPairView, TokenRefreshView, TokenVerifyView,
)

API_V1 = 'api/v1/'

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),

    # Standard JWT auth
    path(API_V1 + 'auth/token/',         TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path(API_V1 + 'auth/token/refresh/', TokenRefreshView.as_view(),   name='token_refresh'),
    path(API_V1 + 'auth/token/verify/',  TokenVerifyView.as_view(),    name='token_verify'),

    # Sprint 8: Combined 2FA login (replaces standard token for enforced roles)
    path(API_V1 + 'auth/token/2fa/',     include('apps.totp.urls')),

    # App APIs (Sprints 1–7, preserved)
    path(API_V1 + 'core/',       include('apps.core.urls')),
    path(API_V1 + 'edms/',       include('apps.edms.urls')),
    path(API_V1 + 'workflow/',   include('apps.workflow.urls')),
    path(API_V1 + 'ocr/',        include('apps.ocr.urls')),
    path(API_V1 + 'audit/',      include('apps.audit.urls')),
    path(API_V1 + 'dashboard/',  include('apps.dashboard.urls')),
    path(API_V1 + 'ml/',         include('apps.ml_classifier.urls')),
    path(API_V1 + 'pdf/',        include('apps.pdf_tools.urls')),
    path(API_V1 + 'sanity/',     include('apps.sanity.urls')),
    path(API_V1 + 'sharelinks/', include('apps.sharelinks.urls')),
    path(API_V1 + 'webhooks/',   include('apps.webhooks.urls')),

    # Sprint 8: TOTP management
    path(API_V1 + 'totp/',       include('apps.totp.urls')),

    # Sprint 8: PWA Scanner
    path(API_V1 + 'scanner/',    include('apps.scanner.urls')),

    # Sprint 7: Public share-link routes (no auth required)
    path('s/', include(('apps.sharelinks.urls', 'sharelinks'), namespace='sharelinks-public')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

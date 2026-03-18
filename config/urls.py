# =============================================================================
# FILE: config/urls.py
# ADDED: /api/v1/search/ → apps.search.urls
#        (Everything-style instant search: autocomplete + unified endpoints)
# All previous routes preserved verbatim.
# =============================================================================
from django.contrib import admin
from django.urls    import path, include
from django.conf    import settings
from django.conf.urls.static import static
from rest_framework_simplejwt.views import TokenVerifyView
from apps.core.auth_views import (
    CookieTokenObtainPairView,
    CookieTokenRefreshView,
    LogoutView,
    MeView,
)
from apps.sanity.views import health_check

API_V1 = 'api/v1/'

urlpatterns = [
    path('admin/', admin.site.urls),

    # ---- JWT auth -------------------------------------------------------
    path(API_V1 + 'auth/token/',         CookieTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path(API_V1 + 'auth/token/refresh/', CookieTokenRefreshView.as_view(),     name='token_refresh'),
    path(API_V1 + 'auth/token/verify/',  TokenVerifyView.as_view(),            name='token_verify'),
    path(API_V1 + 'auth/logout/',        LogoutView.as_view(),                  name='auth_logout'),
    path(API_V1 + 'auth/me/',            MeView.as_view(),                      name='auth_me'),
    path(API_V1 + 'health/',             health_check,                          name='health-check'),

    # ---- Core apps (inside apps/ package) ------------------------------
    path(API_V1 + 'core/',       include('apps.core.urls')),
    path(API_V1 + 'edms/',       include('apps.edms.urls')),
    path(API_V1 + 'workflow/',   include('apps.workflow.urls')),
    path(API_V1 + 'ocr/',        include('apps.ocr.urls')),
    path(API_V1 + 'audit/',      include('apps.audit.urls')),
    path(API_V1 + 'dashboard/',  include('apps.dashboard.urls')),
    path(API_V1 + 'metadata/',   include('apps.metadata.urls')),
    path(API_V1 + 'versioning/', include('apps.versioning.urls')),
    path(API_V1 + 'ml/',         include('apps.ml_classifier.urls')),
    path(API_V1 + 'pdf/',        include('apps.pdf_tools.urls')),
    path(API_V1 + 'sanity/',     include('apps.sanity.urls')),
    path(API_V1 + 'sharelinks/', include('apps.sharelinks.urls')),
    path(API_V1 + 'webhooks/',   include('apps.webhooks.urls')),
    path(API_V1 + 'scanner/',    include('apps.scanner.urls')),
    path(API_V1 + 'pl-master/',  include('apps.pl_master.urls')),
    path(API_V1 + 'sdr/',        include('apps.sdr.urls')),

    # ---- Instant Search (Everything-style) -----------------------------
    path(API_V1 + 'search/',     include('apps.search.urls')),

    # ---- Work Ledger module --------------------------------------------
    path(API_V1 + 'work-ledger/', include('apps.work_ledger.urls')),

    # ---- Backend standalone apps (backend/ package, NOT apps/) ---------
    path(API_V1 + 'config/',     include('config_mgmt.urls')),
    path(API_V1 + 'prototype/',  include('prototype.urls')),

    # ---- BOM app -------------------------------------------------------
    path(API_V1 + 'bom/',        include('bom.urls')),

    # ---- Sprint 7: public share-link routes ----------------------------
    path('s/', include(('apps.sharelinks.urls', 'sharelinks'), namespace='sharelinks-public')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

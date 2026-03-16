# =============================================================================
# FILE: config/urls.py
# BUG FIX 1: Added missing /api/v1/config/   → config_mgmt.urls
#            Added missing /api/v1/prototype/ → prototype.urls
#            Both apps existed in backend/ but were never wired into URL routing
#            causing every Config Management and Prototype Inspection API call
#            to return HTTP 404.
# BUG FIX 2: Work Ledger prefix changed from 'work/' → 'work-ledger/' to match
#            what workLedgerService.ts calls (BASE = '/work-ledger').
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
    path('admin/', admin.site.urls),

    # ---- JWT auth -------------------------------------------------------
    path(API_V1 + 'auth/token/',         TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path(API_V1 + 'auth/token/refresh/', TokenRefreshView.as_view(),   name='token_refresh'),
    path(API_V1 + 'auth/token/verify/',  TokenVerifyView.as_view(),    name='token_verify'),

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

    # ---- Work Ledger module --------------------------------------------
    # BUG FIX 2: prefix was 'work/' but frontend calls /api/v1/work-ledger/
    path(API_V1 + 'work-ledger/', include('apps.work_ledger.urls')),

    # ---- Backend standalone apps (backend/ package, NOT apps/) ---------
    # BUG FIX 1a: config_mgmt was MISSING — caused 404 on all /api/v1/config/ calls
    path(API_V1 + 'config/',     include('config_mgmt.urls')),

    # BUG FIX 1b: prototype was MISSING — caused 404 on all /api/v1/prototype/ calls
    path(API_V1 + 'prototype/',  include('prototype.urls')),

    # RESTORED: BOM app was MISSING
    path(API_V1 + 'bom/',        include('bom.urls')),

    # ---- Sprint 7: public share-link routes ----------------------------
    path('s/', include(('apps.sharelinks.urls', 'sharelinks'), namespace='sharelinks-public')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# =============================================================================
# FILE: backend/master/urls_pl_master.py
# URL configuration for all PL-related routes.
# Included in edms/urls.py under prefix: api/v1/pl-master/
#
# Full route table:
#   GET/POST          /api/v1/pl-master/
#   GET/PATCH/DELETE  /api/v1/pl-master/{pl_number}/
#   GET               /api/v1/pl-master/{pl_number}/bom/
#   GET/PUT/PATCH     /api/v1/pl-master/{pl_number}/vendor-info/
#   GET/POST          /api/v1/pl-master/{pl_number}/tech-eval-docs/
#   DELETE            /api/v1/pl-master/{pl_number}/tech-eval-docs/{pk}/
#   GET/POST          /api/v1/pl-master/{pl_number}/linked-docs/
#   DELETE            /api/v1/pl-master/{pl_number}/linked-docs/{pk}/
#   GET               /api/v1/pl-master/{pl_number}/linked-docs/search/
#   GET               /api/v1/pl-master/drawings/
#   GET               /api/v1/pl-master/specifications/
#   GET               /api/v1/pl-master/alteration-history/
#   GET               /api/v1/pl-master/agencies/
# =============================================================================
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views_pl_master import PLMasterItemViewSet
from .views_tech_eval  import PLTechEvalDocListView, PLTechEvalDocDetailView
from .views_pl_docs    import (
    PLVendorInfoView, PLLinkedDocListView,
    PLLinkedDocDetailView, PLDocSearchView,
)
# Legacy views wired from master/views.py (drawings, specs, alterations, agencies)
from .views_pl_legacy  import (
    PLDrawingsView, PLSpecificationsView,
    PLAlterationHistoryView, PLAgenciesView,
)

# ── PLMasterItem router ────────────────────────────────────────────────────────
router = DefaultRouter()
router.register('items', PLMasterItemViewSet, basename='pl-master-item')


urlpatterns = [
    # ── PLMasterItem CRUD (router adds list/detail/bom) ──────────────────────────
    # Accessed as  /api/v1/pl-master/          (list/create)
    # and          /api/v1/pl-master/{pl}/      (retrieve/update/delete)
    path('',       PLMasterItemViewSet.as_view({'get':'list',  'post':'create'})),
    path('<str:pl_number>/', PLMasterItemViewSet.as_view(
        {'get':'retrieve', 'patch':'partial_update', 'delete':'destroy'}
    )),
    path('<str:pl_number>/bom/', PLMasterItemViewSet.as_view({'get':'bom'})),

    # ── Vendor Info ─────────────────────────────────────────────────────────────
    path('<str:pl_number>/vendor-info/', PLVendorInfoView.as_view()),

    # ── Tech Eval Documents ─────────────────────────────────────────────────────
    path('<str:pl_number>/tech-eval-docs/',         PLTechEvalDocListView.as_view()),
    path('<str:pl_number>/tech-eval-docs/<int:pk>/', PLTechEvalDocDetailView.as_view()),

    # ── Linked Documents ──────────────────────────────────────────────────────────
    # NOTE: search/ must come BEFORE <int:pk>/ to avoid shadowing
    path('<str:pl_number>/linked-docs/search/', PLDocSearchView.as_view()),
    path('<str:pl_number>/linked-docs/',             PLLinkedDocListView.as_view()),
    path('<str:pl_number>/linked-docs/<int:pk>/',    PLLinkedDocDetailView.as_view()),

    # ── Legacy sub-resource endpoints (drawings, specs, alts, agencies) ────────
    path('drawings/',          PLDrawingsView.as_view()),
    path('specifications/',    PLSpecificationsView.as_view()),
    path('alteration-history/',PLAlterationHistoryView.as_view()),
    path('agencies/',          PLAgenciesView.as_view()),
]

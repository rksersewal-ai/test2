# =============================================================================
# FILE: backend/master/urls_pl_docs.py
# URL patterns for VD/NVD vendor info and PL linked documents
#
# Include in edms/urls.py as:
#   path('api/v1/pl-master/', include('master.urls_pl_docs')),
#
# Routes:
#   GET/PUT/PATCH  /api/v1/pl-master/{pl_number}/vendor-info/
#   GET/POST       /api/v1/pl-master/{pl_number}/linked-docs/
#   DELETE         /api/v1/pl-master/{pl_number}/linked-docs/{pk}/
#   GET            /api/v1/pl-master/{pl_number}/linked-docs/search/
# =============================================================================
from django.urls import path
from .views_pl_docs import (
    PLVendorInfoView, PLLinkedDocListView,
    PLLinkedDocDetailView, PLDocSearchView,
)

urlpatterns = [
    path('<str:pl_number>/vendor-info/',             PLVendorInfoView.as_view(),        name='pl-vendor-info'),
    path('<str:pl_number>/linked-docs/',             PLLinkedDocListView.as_view(),     name='pl-linked-docs-list'),
    path('<str:pl_number>/linked-docs/<int:pk>/',    PLLinkedDocDetailView.as_view(),   name='pl-linked-docs-detail'),
    path('<str:pl_number>/linked-docs/search/',      PLDocSearchView.as_view(),         name='pl-docs-search'),
]

# =============================================================================
# FILE: apps/pl_master/urls.py
# =============================================================================
from django.urls import path
from . import views

urlpatterns = [
    # ── Controlling Agency ──────────────────────────────────────────────────
    path('agencies/',                     views.ControllingAgencyListView.as_view(),   name='pl-agency-list'),

    # ── PL Master ───────────────────────────────────────────────────────────
    path('',                              views.PLMasterListCreateView.as_view(),      name='pl-list-create'),
    path('<str:pl_number>/',              views.PLMasterDetailView.as_view(),           name='pl-detail'),
    path('<str:pl_number>/bom/',          views.PLBOMTreeView.as_view(),               name='pl-bom-tree'),

    # ── Drawings ────────────────────────────────────────────────────────────
    path('drawings/',                     views.DrawingMasterListCreateView.as_view(), name='pl-drawing-list'),
    path('drawings/<str:drawing_number>/', views.DrawingMasterDetailView.as_view(),    name='pl-drawing-detail'),

    # ── Specifications ──────────────────────────────────────────────────────
    path('specs/',                        views.SpecMasterListCreateView.as_view(),    name='pl-spec-list'),
    path('specs/<str:spec_number>/',      views.SpecMasterDetailView.as_view(),        name='pl-spec-detail'),

    # ── Vendor Drawings ─────────────────────────────────────────────────────
    path('vendor-drawings/',              views.VendorDrawingListCreateView.as_view(), name='pl-vendor-drg-list'),

    # ── STR Master ──────────────────────────────────────────────────────────
    path('str/',                          views.STRMasterListCreateView.as_view(),     name='pl-str-list'),

    # ── RDSO References ─────────────────────────────────────────────────────
    path('rdso/',                         views.RDSORefListCreateView.as_view(),       name='pl-rdso-list'),

    # ── Alteration History ──────────────────────────────────────────────────
    path('alteration-history/',           views.AlterationHistoryListView.as_view(),  name='pl-alt-history'),

    # ── M2M Links ───────────────────────────────────────────────────────────
    path('links/drawings/',               views.PLDrawingLinkView.as_view(),           name='pl-link-drawing'),
    path('links/specs/',                  views.PLSpecLinkView.as_view(),              name='pl-link-spec'),
    path('links/standards/',              views.PLStandardLinkView.as_view(),          name='pl-link-standard'),
    path('links/smi/',                    views.PLSMILinkView.as_view(),               name='pl-link-smi'),
    path('links/smi/<int:pk>/',           views.PLSMILinkView.as_view(),               name='pl-link-smi-update'),
]

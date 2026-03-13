# =============================================================================
# FILE: apps/workflow/urls.py
# SPRINT 4: Approval routers registered.
# Sprint 1 routes preserved exactly.
# =============================================================================
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.workflow.views import (
    WorkTypeViewSet, WorkLedgerEntryViewSet,
    ApprovalChainViewSet, ApprovalRequestViewSet,
)

router = DefaultRouter()
router.register(r'work-types',          WorkTypeViewSet,         basename='work-type')
router.register(r'work-ledger',         WorkLedgerEntryViewSet,  basename='work-ledger')
router.register(r'approval-chains',     ApprovalChainViewSet,    basename='approval-chain')
router.register(r'approval-requests',   ApprovalRequestViewSet,  basename='approval-request')

urlpatterns = [
    path('', include(router.urls)),
]

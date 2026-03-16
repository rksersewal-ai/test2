# =============================================================================
# FILE: apps/dashboard/urls.py
# SPRINT 2: Added UserSavedViewViewSet router.
# DashboardStatsView path preserved exactly.
# =============================================================================
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.dashboard.views import DashboardStatsView, DashboardTrendView, UserSavedViewViewSet

router = DefaultRouter()
router.register(r'saved-views', UserSavedViewViewSet, basename='saved-view')

urlpatterns = [
    path('stats/',   DashboardStatsView.as_view(), name='dashboard-stats'),
    path('trends/',  DashboardTrendView.as_view(), name='dashboard-trends'),
    path('',         include(router.urls)),
]

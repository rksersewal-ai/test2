# =============================================================================
# FILE: apps/work_ledger/urls.py  (updated — added report/ endpoint)
# =============================================================================
from django.urls            import path
from rest_framework.routers import DefaultRouter
from .views import (
    WorkCategoryViewSet, WorkEntryViewSet,
    WorkTargetViewSet, MonthlyReportView,
)

router = DefaultRouter()
router.register(r'categories', WorkCategoryViewSet, basename='work-category')
router.register(r'entries',    WorkEntryViewSet,    basename='work-entry')
router.register(r'targets',    WorkTargetViewSet,   basename='work-target')

urlpatterns = [
    path('report/', MonthlyReportView.as_view(), name='work-monthly-report'),
] + router.urls

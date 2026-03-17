# =============================================================================
# FILE: apps/work_ledger/urls.py  (updated — PDF + Excel report endpoints)
# =============================================================================
from django.urls            import path
from rest_framework.routers import DefaultRouter
from .views import (
    WorkCategoryViewSet, WorkEntryViewSet,
    WorkTargetViewSet,
    MonthlyReportView, MonthlyExcelReportView,
    MonthlyKPIReportView, WorkActivityReportView, WorkActivityReportExportView,
)

router = DefaultRouter()
router.register(r'categories', WorkCategoryViewSet, basename='work-category')
router.register(r'entries',    WorkEntryViewSet,    basename='work-entry')
router.register(r'targets',    WorkTargetViewSet,   basename='work-target')

urlpatterns = [
    path('report/kpi/',      MonthlyKPIReportView.as_view(),      name='work-monthly-kpi'),
    path('report/activity/', WorkActivityReportView.as_view(),    name='work-activity-report'),
    path('report/export/',   WorkActivityReportExportView.as_view(), name='work-activity-export'),
    path('report/',       MonthlyReportView.as_view(),      name='work-monthly-report'),
    path('report/excel/', MonthlyExcelReportView.as_view(), name='work-monthly-report-excel'),
] + router.urls

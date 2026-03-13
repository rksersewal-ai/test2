from django.urls import path
from . import views

urlpatterns = [
    path("categories/",          views.WorkCategoryListView.as_view(),           name="wl-categories"),
    path("entries/",             views.WorkLedgerListCreateView.as_view(),        name="wl-entry-list-create"),
    path("entries/<int:work_id>/", views.WorkLedgerDetailView.as_view(),          name="wl-entry-detail"),
    path("dashboard/monthly-summary/", views.WorkLedgerDashboardView.as_view(),  name="wl-dashboard"),
    path("reports/activity/",    views.WorkActivityReportView.as_view(),          name="wl-report-activity"),
    path("reports/monthly-kpi/", views.WorkMonthlyKpiView.as_view(),              name="wl-report-kpi"),
    path("reports/activity/export/", views.WorkActivityReportExportView.as_view(), name="wl-report-export"),
]

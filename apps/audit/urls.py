from django.urls import path
from apps.audit.views import AuditLogListView, AuditLogDetailView, DocumentAccessLogListView

urlpatterns = [
    path('logs/', AuditLogListView.as_view(), name='audit-log-list'),
    path('logs/<int:pk>/', AuditLogDetailView.as_view(), name='audit-log-detail'),
    path('document-access/', DocumentAccessLogListView.as_view(), name='document-access-log-list'),
]

from django.urls import path
from apps.scanner.views import ScanView, ScanAndSearchView

urlpatterns = [
    path('scan/',            ScanView.as_view(),          name='scanner-scan'),
    path('scan-and-search/', ScanAndSearchView.as_view(), name='scanner-scan-search'),
]

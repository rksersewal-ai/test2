# =============================================================================
# FILE: apps/sdr/urls.py  (updated — added analytics/ endpoint)
# =============================================================================
from django.urls            import path
from rest_framework.routers import DefaultRouter
from .views import (
    SDRRequestViewSet, SDRResponseViewSet,
    SDRAttachmentViewSet, SDRAnalyticsView,
)

router = DefaultRouter()
router.register(r'requests',    SDRRequestViewSet,    basename='sdr-request')
router.register(r'responses',   SDRResponseViewSet,   basename='sdr-response')
router.register(r'attachments', SDRAttachmentViewSet, basename='sdr-attachment')

urlpatterns = [
    path('analytics/', SDRAnalyticsView.as_view(), name='sdr-analytics'),
] + router.urls

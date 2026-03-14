# =============================================================================
# FILE: apps/sdr/urls.py
# =============================================================================
from rest_framework.routers import DefaultRouter
from .views import SDRRequestViewSet, SDRResponseViewSet, SDRAttachmentViewSet

router = DefaultRouter()
router.register(r'requests',    SDRRequestViewSet,    basename='sdr-request')
router.register(r'responses',   SDRResponseViewSet,   basename='sdr-response')
router.register(r'attachments', SDRAttachmentViewSet, basename='sdr-attachment')

urlpatterns = router.urls

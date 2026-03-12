from rest_framework.routers import DefaultRouter
from apps.ocr.views import OCRQueueViewSet

router = DefaultRouter()
router.register(r'ocr-queue', OCRQueueViewSet, basename='ocr-queue')

urlpatterns = router.urls

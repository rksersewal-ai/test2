from rest_framework.routers import DefaultRouter
from django.urls import path, include
from apps.ocr.views import OCRQueueViewSet, OCRResultListView, OCRResultDetailView

router = DefaultRouter()
router.register(r'queue', OCRQueueViewSet, basename='ocr-queue')

urlpatterns = [
    path('', include(router.urls)),
    path('results/', OCRResultListView.as_view(), name='ocr-result-list'),
    path('results/<int:pk>/', OCRResultDetailView.as_view(), name='ocr-result-detail'),
]

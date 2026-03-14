from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import OCRJobViewSet

router = DefaultRouter()
router.register('queue', OCRJobViewSet, basename='ocr-job')

urlpatterns = [
    path('', include(router.urls)),
]

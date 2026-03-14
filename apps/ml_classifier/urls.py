# =============================================================================
# FILE: apps/ml_classifier/urls.py
# SPRINT 5
# =============================================================================
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.ml_classifier.views import ClassifierModelViewSet, ClassificationResultViewSet

router = DefaultRouter()
router.register(r'models',  ClassifierModelViewSet,       basename='ml-model')
router.register(r'results', ClassificationResultViewSet,  basename='ml-result')

urlpatterns = [
    path('', include(router.urls)),
]

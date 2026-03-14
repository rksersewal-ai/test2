from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import InspectionViewSet, PunchItemViewSet

router = DefaultRouter()
router.register('inspections', InspectionViewSet, basename='inspection')
router.register('punch-items', PunchItemViewSet,  basename='punch-item')

urlpatterns = [
    path('', include(router.urls)),
]

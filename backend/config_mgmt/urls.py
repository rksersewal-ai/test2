from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import LocoConfigViewSet, ECNViewSet

router = DefaultRouter()
router.register('configs', LocoConfigViewSet, basename='loco-config')
router.register('ecn',     ECNViewSet,        basename='ecn')

urlpatterns = [
    path('', include(router.urls)),
]

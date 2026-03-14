from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.sanity.views import SanityReportViewSet

router = DefaultRouter()
router.register(r'reports', SanityReportViewSet, basename='sanity-report')

urlpatterns = [
    path('', include(router.urls)),
]

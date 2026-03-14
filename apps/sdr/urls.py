# =============================================================================
# FILE: apps/sdr/urls.py
# =============================================================================
from django.urls            import path
from rest_framework.routers import DefaultRouter
from .views import SDRRecordViewSet, DrawingSpecSearchView

router = DefaultRouter()
router.register(r'', SDRRecordViewSet, basename='sdr')

urlpatterns = [
    path('search/', DrawingSpecSearchView.as_view(), name='sdr-doc-search'),
] + router.urls

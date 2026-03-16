from rest_framework.routers import DefaultRouter
from .views import MetadataFieldViewSet, DocumentMetadataViewSet, MetadataHistoryViewSet

router = DefaultRouter()
router.register(r'fields',  MetadataFieldViewSet,    basename='metadata-field')
router.register(r'values',  DocumentMetadataViewSet, basename='metadata-value')
router.register(r'history', MetadataHistoryViewSet,  basename='metadata-history')

urlpatterns = router.urls

from rest_framework.routers import DefaultRouter
from .views import (
    DocumentVersionViewSet, AlterationHistoryViewSet,
    VersionAnnotationViewSet, VersionDiffViewSet,
)

router = DefaultRouter()
router.register(r'versions',     DocumentVersionViewSet,   basename='doc-version')
router.register(r'alterations',  AlterationHistoryViewSet, basename='alteration-history')
router.register(r'annotations',  VersionAnnotationViewSet, basename='version-annotation')
router.register(r'diffs',        VersionDiffViewSet,       basename='version-diff')

urlpatterns = router.urls

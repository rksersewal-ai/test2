from rest_framework.routers import DefaultRouter
from .views import DocumentVersionViewSet, VersionAnnotationViewSet, VersionDiffViewSet

router = DefaultRouter()
router.register(r'versions',     DocumentVersionViewSet,  basename='doc-version')
router.register(r'annotations',  VersionAnnotationViewSet, basename='version-annotation')
router.register(r'diffs',        VersionDiffViewSet,      basename='version-diff')

urlpatterns = router.urls

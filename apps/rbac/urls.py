from rest_framework.routers import DefaultRouter
from .views import UserRoleViewSet, DocumentPermissionOverrideViewSet

router = DefaultRouter()
router.register(r'roles',     UserRoleViewSet,                basename='user-role')
router.register(r'overrides', DocumentPermissionOverrideViewSet, basename='doc-perm-override')

urlpatterns = router.urls

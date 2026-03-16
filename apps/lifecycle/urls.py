from rest_framework.routers import DefaultRouter
from .views import RetentionPolicyViewSet, DocumentLifecycleViewSet, LifecycleEventViewSet

router = DefaultRouter()
router.register(r'policies',  RetentionPolicyViewSet,    basename='retention-policy')
router.register(r'documents', DocumentLifecycleViewSet,  basename='doc-lifecycle')
router.register(r'events',    LifecycleEventViewSet,     basename='lifecycle-event')

urlpatterns = router.urls

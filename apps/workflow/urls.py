from rest_framework.routers import DefaultRouter
from apps.workflow.views import WorkTypeViewSet, WorkLedgerEntryViewSet

router = DefaultRouter()
router.register(r'work-types', WorkTypeViewSet, basename='work-type')
router.register(r'work-ledger', WorkLedgerEntryViewSet, basename='work-ledger')

urlpatterns = router.urls

# =============================================================================
# FILE: apps/work_ledger/urls.py
# =============================================================================
from rest_framework.routers import DefaultRouter
from .views import WorkCategoryViewSet, WorkEntryViewSet, WorkTargetViewSet

router = DefaultRouter()
router.register(r'categories', WorkCategoryViewSet, basename='workcategory')
router.register(r'entries',    WorkEntryViewSet,    basename='workentry')
router.register(r'targets',    WorkTargetViewSet,   basename='worktarget')

urlpatterns = router.urls

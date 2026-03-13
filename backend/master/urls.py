from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    LocomotiveTypeViewSet, ComponentCatalogViewSet,
    LookupCategoryViewSet, MasterDataChangeLogViewSet, MasterDataSummaryView,
)

router = DefaultRouter()
router.register('locos',      LocomotiveTypeViewSet,       basename='loco')
router.register('components', ComponentCatalogViewSet,     basename='component')
router.register('lookups',    LookupCategoryViewSet,       basename='lookup')
router.register('changelog',  MasterDataChangeLogViewSet,  basename='master-changelog')
router.register('summary',    MasterDataSummaryView,       basename='master-summary')

urlpatterns = [
    path('', include(router.urls)),
]

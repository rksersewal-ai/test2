from rest_framework.routers import DefaultRouter
from django.urls import path, include
from apps.workflow.views import WorkLedgerViewSet, WorkTypeViewSet, VendorViewSet, TenderViewSet

router = DefaultRouter()
router.register(r'work-ledger', WorkLedgerViewSet, basename='work-ledger')
router.register(r'work-types', WorkTypeViewSet, basename='work-types')
router.register(r'vendors', VendorViewSet, basename='vendors')
router.register(r'tenders', TenderViewSet, basename='tenders')

urlpatterns = [path('', include(router.urls))]

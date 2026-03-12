from rest_framework.routers import DefaultRouter
from django.urls import path, include
from apps.edms.views import DocumentViewSet, RevisionViewSet, CategoryViewSet, DocumentTypeViewSet

router = DefaultRouter()
router.register(r'documents', DocumentViewSet, basename='documents')
router.register(r'revisions', RevisionViewSet, basename='revisions')
router.register(r'categories', CategoryViewSet, basename='categories')
router.register(r'document-types', DocumentTypeViewSet, basename='document-types')

urlpatterns = [path('', include(router.urls))]

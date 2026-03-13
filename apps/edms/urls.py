# =============================================================================
# FILE: apps/edms/urls.py
# SPRINT 1: Registered new routers for Custom Fields, Correspondents, Notes.
# =============================================================================
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.edms import views

router = DefaultRouter()
router.register(r'documents',              views.DocumentViewSet,               basename='document')
router.register(r'revisions',              views.RevisionViewSet,               basename='revision')
router.register(r'categories',             views.CategoryViewSet,               basename='category')
router.register(r'document-types',         views.DocumentTypeViewSet,           basename='document-type')

# Sprint 1 additions
router.register(r'custom-field-definitions', views.CustomFieldDefinitionViewSet, basename='custom-field-definition')
router.register(r'correspondents',           views.CorrespondentViewSet,          basename='correspondent')
router.register(r'correspondent-links',      views.DocumentCorrespondentLinkViewSet, basename='correspondent-link')
router.register(r'notes',                    views.DocumentNoteViewSet,           basename='document-note')

urlpatterns = [
    path('', include(router.urls)),
]

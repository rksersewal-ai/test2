# =============================================================================
# FILE: apps/sharelinks/urls.py
# SPRINT 7
# =============================================================================
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.sharelinks.views  import (
    ShareLinkViewSet, PublicDocumentView,
    PublicDownloadView, PublicPasswordVerifyView,
)

router = DefaultRouter()
router.register(r'', ShareLinkViewSet, basename='sharelink')

urlpatterns = [
    path('', include(router.urls)),
]

# Public URL patterns (mounted at /s/ in config/urls.py)
public_urlpatterns = [
    path('<str:token>/',          PublicDocumentView.as_view(),         name='public-share'),
    path('<str:token>/download/', PublicDownloadView.as_view(),         name='public-share-download'),
    path('<str:token>/verify/',   PublicPasswordVerifyView.as_view(),   name='public-share-verify'),
]

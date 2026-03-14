from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.pdf_tools.views import PdfJobViewSet

router = DefaultRouter()
router.register(r'', PdfJobViewSet, basename='pdf')

urlpatterns = [
    path('', include(router.urls)),
]

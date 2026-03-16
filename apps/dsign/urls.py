from rest_framework.routers import DefaultRouter
from .views import SigningCertificateViewSet, DocumentSignatureViewSet

router = DefaultRouter()
router.register(r'certificates', SigningCertificateViewSet, basename='signing-cert')
router.register(r'signatures',   DocumentSignatureViewSet,  basename='doc-signature')

urlpatterns = router.urls

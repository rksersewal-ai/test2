from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import SigningCertificate, DocumentSignature
from .serializers import SigningCertificateSerializer, DocumentSignatureSerializer
from .services import DigitalSignatureService
from apps.edms.models import Document
from apps.versioning.models import DocumentVersion


class SigningCertificateViewSet(viewsets.ModelViewSet):
    serializer_class   = SigningCertificateSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return SigningCertificate.objects.filter(user=self.request.user)


class DocumentSignatureViewSet(viewsets.ReadOnlyModelViewSet):
    queryset           = DocumentSignature.objects.select_related('document', 'signed_by', 'certificate')
    serializer_class   = DocumentSignatureSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        qs     = super().get_queryset()
        doc_id = self.request.query_params.get('document')
        if doc_id:
            qs = qs.filter(document_id=doc_id)
        return qs

    @action(detail=False, methods=['post'], url_path='sign')
    def sign(self, request):
        """POST /signatures/sign/ — sign a document."""
        doc_id      = request.data.get('document')
        version_id  = request.data.get('version')
        private_key = request.data.get('private_key_pem', '')
        role        = request.data.get('role', DocumentSignature.SignatureRole.APPROVED)
        remarks     = request.data.get('remarks', '')
        try:
            document = Document.objects.get(pk=doc_id)
        except Document.DoesNotExist:
            return Response({'error': 'Document not found'}, status=status.HTTP_404_NOT_FOUND)
        version = None
        if version_id:
            try:
                version = DocumentVersion.objects.get(pk=version_id)
            except DocumentVersion.DoesNotExist:
                return Response({'error': 'Version not found'}, status=status.HTTP_404_NOT_FOUND)
        try:
            sig = DigitalSignatureService.sign_document(
                document, request.user, private_key, role, version, remarks
            )
        except (ValueError, RuntimeError) as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(DocumentSignatureSerializer(sig).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'], url_path='verify')
    def verify(self, request, pk=None):
        """POST /signatures/<id>/verify/ — re-verify a signature."""
        try:
            sig = DocumentSignature.objects.get(pk=pk)
        except DocumentSignature.DoesNotExist:
            return Response({'error': 'Signature not found'}, status=status.HTTP_404_NOT_FOUND)
        valid = DigitalSignatureService.verify_signature(sig)
        return Response({'valid': valid, 'status': sig.status})

    @action(detail=True, methods=['post'], url_path='revoke')
    def revoke(self, request, pk=None):
        """POST /signatures/<id>/revoke/ — revoke a signature."""
        try:
            sig = DocumentSignature.objects.get(pk=pk)
        except DocumentSignature.DoesNotExist:
            return Response({'error': 'Signature not found'}, status=status.HTTP_404_NOT_FOUND)
        reason = request.data.get('reason', '')
        DigitalSignatureService.revoke(sig, reason)
        return Response({'status': 'revoked'})

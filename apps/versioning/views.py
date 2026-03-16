# =============================================================================
# FILE: apps/versioning/views.py
# FR-006: API views for document versioning
# =============================================================================
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import DocumentVersion, VersionAnnotation, VersionDiff
from .serializers import DocumentVersionSerializer, VersionAnnotationSerializer, VersionDiffSerializer
from .services import VersioningService
from apps.edms.models import Document


class DocumentVersionViewSet(viewsets.ReadOnlyModelViewSet):
    """List and retrieve version history for documents."""
    queryset           = DocumentVersion.objects.select_related('document', 'created_by')
    serializer_class   = DocumentVersionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        qs = super().get_queryset()
        doc_id = self.request.query_params.get('document')
        if doc_id:
            qs = qs.filter(document_id=doc_id)
        # Exclude deleted by default
        if not self.request.query_params.get('include_deleted'):
            qs = qs.exclude(status=DocumentVersion.VersionStatus.DELETED)
        return qs.order_by('-created_at')

    @action(detail=False, methods=['post'], url_path='rollback')
    def rollback(self, request):
        """POST /versions/rollback/ — roll back document to a previous version."""
        doc_id    = request.data.get('document')
        version_n = request.data.get('version_number')
        reason    = request.data.get('reason', '')
        try:
            document = Document.objects.get(pk=doc_id)
        except Document.DoesNotExist:
            return Response({'error': 'Document not found'}, status=status.HTTP_404_NOT_FOUND)
        try:
            rolled = VersioningService.rollback(document, version_n, user=request.user, reason=reason)
        except DocumentVersion.DoesNotExist:
            return Response({'error': f'Version {version_n} not found'}, status=status.HTTP_404_NOT_FOUND)
        return Response(DocumentVersionSerializer(rolled).data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['post'], url_path='recover')
    def recover(self, request):
        """POST /versions/recover/ — recover a soft-deleted version (within 30 days)."""
        version_id = request.data.get('version_id')
        try:
            version = DocumentVersion.objects.get(pk=version_id)
            VersioningService.recover(version)
        except DocumentVersion.DoesNotExist:
            return Response({'error': 'Version not found'}, status=status.HTTP_404_NOT_FOUND)
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response({'status': 'recovered', 'version': str(version)})

    @action(detail=False, methods=['get'], url_path='compare')
    def compare(self, request):
        """GET /versions/compare/?from=<id>&to=<id> — diff two versions."""
        from_id = request.query_params.get('from')
        to_id   = request.query_params.get('to')
        try:
            v_from = DocumentVersion.objects.get(pk=from_id)
            v_to   = DocumentVersion.objects.get(pk=to_id)
        except DocumentVersion.DoesNotExist:
            return Response({'error': 'Version not found'}, status=status.HTTP_404_NOT_FOUND)
        diff = VersioningService.compare(v_from, v_to)
        return Response({'diff': diff, 'from': str(v_from), 'to': str(v_to)})


class VersionAnnotationViewSet(viewsets.ModelViewSet):
    queryset           = VersionAnnotation.objects.select_related('version', 'created_by')
    serializer_class   = VersionAnnotationSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class VersionDiffViewSet(viewsets.ReadOnlyModelViewSet):
    queryset           = VersionDiff.objects.select_related('from_version', 'to_version')
    serializer_class   = VersionDiffSerializer
    permission_classes = [IsAuthenticated]

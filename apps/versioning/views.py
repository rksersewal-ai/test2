from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import DocumentVersion, AlterationHistory, VersionAnnotation, VersionDiff
from .serializers import (
    DocumentVersionSerializer, AlterationHistorySerializer,
    VersionAnnotationSerializer, VersionDiffSerializer,
)
from .services import VersioningService
from apps.edms.models import Document


class DocumentVersionViewSet(viewsets.ReadOnlyModelViewSet):
    queryset           = DocumentVersion.objects.select_related('document', 'created_by')
    serializer_class   = DocumentVersionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        qs     = super().get_queryset()
        doc_id = self.request.query_params.get('document')
        if doc_id:
            qs = qs.filter(document_id=doc_id)
        if not self.request.query_params.get('include_deleted'):
            qs = qs.exclude(status=DocumentVersion.VersionStatus.DELETED)
        return qs.order_by('-created_at')

    @action(detail=False, methods=['post'], url_path='rollback')
    def rollback(self, request):
        doc_id    = request.data.get('document')
        version_n = request.data.get('version_number')
        reason    = request.data.get('reason', '')
        try:
            document = Document.objects.get(pk=doc_id)
        except Document.DoesNotExist:
            return Response({'error': 'Document not found'}, status=status.HTTP_404_NOT_FOUND)
        try:
            rolled = VersioningService.rollback(document, version_n,
                                                user=request.user, reason=reason)
        except DocumentVersion.DoesNotExist:
            return Response({'error': f'Version {version_n} not found'},
                            status=status.HTTP_404_NOT_FOUND)
        return Response(DocumentVersionSerializer(rolled).data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['post'], url_path='recover')
    def recover(self, request):
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
        from_id = request.query_params.get('from')
        to_id   = request.query_params.get('to')
        try:
            v_from = DocumentVersion.objects.get(pk=from_id)
            v_to   = DocumentVersion.objects.get(pk=to_id)
        except DocumentVersion.DoesNotExist:
            return Response({'error': 'Version not found'}, status=status.HTTP_404_NOT_FOUND)
        diff = VersioningService.compare(v_from, v_to)
        return Response({'diff': diff, 'from': str(v_from), 'to': str(v_to)})


class AlterationHistoryViewSet(viewsets.ModelViewSet):
    """PRD Table 13.9: alteration history per document."""
    queryset           = AlterationHistory.objects.select_related(
        'document', 'version', 'implemented_by', 'created_by'
    )
    serializer_class   = AlterationHistorySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        qs     = super().get_queryset()
        doc_id = self.request.query_params.get('document')
        agency = self.request.query_params.get('source_agency')
        status_filter = self.request.query_params.get('implementation_status')
        if doc_id:
            qs = qs.filter(document_id=doc_id)
        if agency:
            qs = qs.filter(source_agency=agency)
        if status_filter:
            qs = qs.filter(implementation_status=status_filter)
        return qs


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

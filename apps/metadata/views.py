# =============================================================================
# FILE: apps/metadata/views.py
# FR-005: API views for metadata fields, values, history, and export
# =============================================================================
from django.http import HttpResponse
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import MetadataField, DocumentMetadata, MetadataHistory
from .serializers import MetadataFieldSerializer, DocumentMetadataSerializer, MetadataHistorySerializer
from .services import MetadataService
from apps.edms.models import Document


class MetadataFieldViewSet(viewsets.ModelViewSet):
    """CRUD for metadata field definitions per document type."""
    queryset           = MetadataField.objects.filter(is_active=True).select_related('document_type')
    serializer_class   = MetadataFieldSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        qs = super().get_queryset()
        doc_type = self.request.query_params.get('document_type')
        if doc_type:
            qs = qs.filter(document_type_id=doc_type)
        return qs


class DocumentMetadataViewSet(viewsets.ModelViewSet):
    """Manage metadata values for a specific document."""
    queryset           = DocumentMetadata.objects.select_related('document', 'field')
    serializer_class   = DocumentMetadataSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        qs = super().get_queryset()
        doc_id = self.request.query_params.get('document')
        if doc_id:
            qs = qs.filter(document_id=doc_id)
        return qs

    @action(detail=False, methods=['post'], url_path='bulk-set')
    def bulk_set(self, request):
        """POST /metadata/values/bulk-set/ — set multiple fields at once."""
        doc_id = request.data.get('document')
        values = request.data.get('values', {})
        try:
            document = Document.objects.get(pk=doc_id)
        except Document.DoesNotExist:
            return Response({'error': 'Document not found'}, status=status.HTTP_404_NOT_FOUND)
        results = MetadataService.bulk_set(document, values, user=request.user)
        return Response({'updated': len(results)})

    @action(detail=False, methods=['get'], url_path='export')
    def export(self, request):
        """GET /metadata/values/export/?document=<id>&format=csv|json"""
        doc_id     = request.query_params.get('document')
        fmt        = request.query_params.get('format', 'csv')
        try:
            document = Document.objects.get(pk=doc_id)
        except Document.DoesNotExist:
            return Response({'error': 'Document not found'}, status=status.HTTP_404_NOT_FOUND)
        if fmt == 'json':
            data = MetadataService.export_json(document)
            return HttpResponse(data, content_type='application/json')
        data = MetadataService.export_csv(document)
        resp = HttpResponse(data, content_type='text/csv')
        resp['Content-Disposition'] = (
            f'attachment; filename="metadata_{document.document_number}.csv"'
        )
        return resp


class MetadataHistoryViewSet(viewsets.ReadOnlyModelViewSet):
    """Read-only history of metadata changes for compliance audit."""
    queryset           = MetadataHistory.objects.select_related('metadata__document', 'metadata__field', 'changed_by')
    serializer_class   = MetadataHistorySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        qs = super().get_queryset()
        doc_id     = self.request.query_params.get('document')
        field_name = self.request.query_params.get('field_name')
        if doc_id:
            qs = qs.filter(metadata__document_id=doc_id)
        if field_name:
            qs = qs.filter(metadata__field__field_name=field_name)
        return qs

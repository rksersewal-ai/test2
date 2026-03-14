# =============================================================================
# FILE: apps/pl_master/views_alteration.py
#
# AlterationHistory read-only API with filters.
# =============================================================================
from rest_framework import viewsets, filters
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators  import action
from rest_framework.response    import Response
from django_filters.rest_framework import DjangoFilterBackend

from apps.pl_master.models import AlterationHistory
from apps.pl_master.serializers import AlterationHistorySerializer


class AlterationHistoryViewSet(viewsets.ReadOnlyModelViewSet):
    """
    GET /api/v1/pl-master/alterations/
    GET /api/v1/pl-master/alterations/{id}/
    GET /api/v1/pl-master/alterations/pending/        -- implementation_status=PENDING
    GET /api/v1/pl-master/alterations/by-document/?doc=CLW/ED/SK/WAP7-1234

    Filters: document_type, source_agency, implementation_status, alteration_date
    Search:  document_number, alteration_number, changes_description
    """
    permission_classes = [IsAuthenticated]
    filter_backends    = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_fields   = [
        'document_type',
        'source_agency',
        'implementation_status',
    ]
    search_fields      = [
        'document_number',
        'alteration_number',
        'changes_description',
        'probable_impacts',
    ]
    ordering_fields    = ['alteration_date', 'created_at', 'document_type']
    ordering           = ['-alteration_date']

    def get_queryset(self):
        qs = AlterationHistory.objects.all()
        # date range filters
        date_from = self.request.query_params.get('date_from')
        date_to   = self.request.query_params.get('date_to')
        if date_from:
            qs = qs.filter(alteration_date__gte=date_from)
        if date_to:
            qs = qs.filter(alteration_date__lte=date_to)
        return qs

    @action(detail=False, methods=['get'], url_path='pending')
    def pending(self, request):
        qs = self.get_queryset().filter(implementation_status='PENDING')
        serializer = AlterationHistorySerializer(qs, many=True)
        return Response({'count': qs.count(), 'results': serializer.data})

    @action(detail=False, methods=['get'], url_path='by-document')
    def by_document(self, request):
        doc = request.query_params.get('doc', '')
        if not doc:
            return Response({'error': 'doc query param required'}, status=400)
        qs = self.get_queryset().filter(document_number__icontains=doc)
        serializer = AlterationHistorySerializer(qs, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'], url_path='mark-implemented')
    def mark_implemented(self, request, pk=None):
        """Allow Officer/WM to mark an alteration as implemented."""
        obj = self.get_object()
        obj.implementation_status = 'IMPLEMENTED'
        obj.implementation_remarks = request.data.get('remarks', '')
        obj.save(update_fields=['implementation_status', 'implementation_remarks'])
        return Response(AlterationHistorySerializer(obj).data)

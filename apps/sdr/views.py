# =============================================================================
# FILE: apps/sdr/views.py
# =============================================================================
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, filters
from rest_framework.permissions import IsAuthenticated
from rest_framework.response    import Response
from rest_framework.views       import APIView

from .models      import SDRRecord
from .serializers import SDRRecordSerializer, SDRRecordListSerializer


class SDRRecordViewSet(viewsets.ModelViewSet):
    """
    CRUD for SDR Records.

    GET    /api/v1/sdr/                    — list (lightweight)
    POST   /api/v1/sdr/                    — create new issue record + items
    GET    /api/v1/sdr/{id}/               — full detail with items
    PUT    /api/v1/sdr/{id}/               — full update (replaces all items)
    PATCH  /api/v1/sdr/{id}/               — partial update
    DELETE /api/v1/sdr/{id}/               — delete

    Filters: shop_name, issuing_official, issue_date
    Search:  sdr_number, shop_name, requesting_official, receiving_official
    """
    permission_classes = [IsAuthenticated]
    filter_backends    = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_fields  = ['shop_name', 'issuing_official', 'issue_date']
    search_fields     = [
        'sdr_number', 'shop_name',
        'requesting_official', 'receiving_official',
        'items__document_number',
    ]
    ordering_fields   = ['issue_date', 'created_at', 'shop_name']
    ordering          = ['-issue_date']

    def get_queryset(self):
        return SDRRecord.objects.prefetch_related(
            'items__drawing', 'items__specification'
        ).select_related('created_by')

    def get_serializer_class(self):
        if self.action == 'list':
            return SDRRecordListSerializer
        return SDRRecordSerializer

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class DrawingSpecSearchView(APIView):
    """
    Typeahead search for drawings and specifications.
    Used by the SDR form when the user types a document number.

    GET /api/v1/sdr/search/?q=WAP7&type=DRAWING
    GET /api/v1/sdr/search/?q=RDSO/PE&type=SPEC
    GET /api/v1/sdr/search/?q=WAP7          — returns both types

    Returns: [{id, type, number, title, current_alteration, size_options}]
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        q        = request.query_params.get('q', '').strip()
        doc_type = request.query_params.get('type', '').upper()

        if len(q) < 2:
            return Response([])

        results = []

        if doc_type in ('DRAWING', ''):
            from apps.pl_master.models import DrawingMaster
            drgs = (
                DrawingMaster.objects
                .filter(drawing_number__icontains=q, is_active=True)
                .values('id', 'drawing_number', 'drawing_title', 'current_alteration', 'drawing_type')
                [:20]
            )
            for d in drgs:
                results.append({
                    'id':                d['id'],
                    'type':             'DRAWING',
                    'number':           d['drawing_number'],
                    'title':            d['drawing_title'] or '',
                    'current_alteration': d['current_alteration'] or '',
                })

        if doc_type in ('SPEC', ''):
            from apps.pl_master.models import SpecificationMaster
            specs = (
                SpecificationMaster.objects
                .filter(spec_number__icontains=q, is_active=True)
                .values('id', 'spec_number', 'spec_title', 'current_alteration')
                [:20]
            )
            for s in specs:
                results.append({
                    'id':                s['id'],
                    'type':             'SPEC',
                    'number':           s['spec_number'],
                    'title':            s['spec_title'] or '',
                    'current_alteration': s['current_alteration'] or '',
                })

        return Response(results)

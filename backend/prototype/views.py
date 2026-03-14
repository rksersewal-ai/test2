# =============================================================================
# FILE: backend/prototype/views.py
# =============================================================================
from django.db.models import Count
from django.utils import timezone
from rest_framework import viewsets, permissions, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend

from .models import Inspection, PunchItem
from .serializers import InspectionSerializer, InspectionListSerializer, PunchItemSerializer


class InspectionViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    filter_backends    = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields   = ['status', 'inspection_type', 'loco_class']
    search_fields      = ['loco_number', 'loco_class', 'inspector']
    ordering_fields    = ['inspection_date', 'created_at', 'status']

    def get_queryset(self):
        return (
            Inspection.objects
            .select_related('created_by')
            .annotate(open_punch_count=Count(
                'punch_items', filter=__import__('django.db.models', fromlist=['Q']).Q(punch_items__status='Open')
            ))
            .prefetch_related('punch_items__closed_by')
        )

    def get_serializer_class(self):
        if self.action == 'list':
            return InspectionListSerializer
        return InspectionSerializer

    @action(detail=True, methods=['post'], url_path='close')
    def close_inspection(self, request, pk=None):
        """POST /api/prototype/inspections/:id/close/ — close entire inspection."""
        inspection = self.get_object()
        inspection.status = 'Closed'
        inspection.save(update_fields=['status'])
        return Response(InspectionSerializer(inspection, context={'request': request}).data)

    @action(detail=True, methods=['post'], url_path='punch-items')
    def add_punch_item(self, request, pk=None):
        """POST /api/prototype/inspections/:id/punch-items/ — add a punch item."""
        inspection = self.get_object()
        serializer = PunchItemSerializer(data={
            **request.data,
            'inspection': inspection.id
        }, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=201)


class PunchItemViewSet(viewsets.ModelViewSet):
    queryset = PunchItem.objects.select_related('inspection', 'closed_by').all()
    serializer_class = PunchItemSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends  = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['inspection', 'status']
    ordering_fields  = ['created_at']

    @action(detail=True, methods=['post'], url_path='close')
    def close_item(self, request, pk=None):
        """POST /api/prototype/punch-items/:id/close/ — close a punch item."""
        item = self.get_object()
        item.status    = 'Closed'
        item.closed_by = request.user
        item.closed_at = timezone.now()
        item.remarks   = request.data.get('remarks', item.remarks)
        item.save(update_fields=['status', 'closed_by', 'closed_at', 'remarks'])
        return Response(PunchItemSerializer(item, context={'request': request}).data)

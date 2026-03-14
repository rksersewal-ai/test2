# =============================================================================
# FILE: backend/config_mgmt/views.py
# =============================================================================
from django.utils import timezone
from rest_framework import viewsets, permissions, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend

from .models import LocoConfig, ECN
from .serializers import LocoConfigSerializer, ECNSerializer


class LocoConfigViewSet(viewsets.ModelViewSet):
    queryset = LocoConfig.objects.select_related('created_by').all()
    serializer_class = LocoConfigSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends  = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['loco_class', 'status']
    search_fields    = ['serial_no', 'ecn_ref', 'config_version', 'changed_by']
    ordering_fields  = ['created_at', 'loco_class', 'serial_no', 'effective_date']


class ECNViewSet(viewsets.ModelViewSet):
    queryset = ECN.objects.select_related('raised_by', 'approved_by').all()
    serializer_class = ECNSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends  = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['loco_class', 'status']
    search_fields    = ['ecn_number', 'subject', 'description']
    ordering_fields  = ['created_at', 'date', 'status']

    @action(detail=True, methods=['post'], url_path='approve')
    def approve(self, request, pk=None):
        """POST /api/config/ecn/:id/approve/ — approve a PENDING ECN."""
        ecn = self.get_object()
        if ecn.status != 'PENDING':
            return Response({'detail': f'ECN is already {ecn.status}.'}, status=400)
        ecn.status      = 'APPROVED'
        ecn.approved_by = request.user
        ecn.approved_at = timezone.now()
        ecn.save(update_fields=['status', 'approved_by', 'approved_at'])
        return Response(ECNSerializer(ecn, context={'request': request}).data)

    @action(detail=True, methods=['post'], url_path='reject')
    def reject(self, request, pk=None):
        """POST /api/config/ecn/:id/reject/ — reject a PENDING ECN."""
        ecn = self.get_object()
        if ecn.status not in ('PENDING',):
            return Response({'detail': f'Cannot reject — status is {ecn.status}.'}, status=400)
        ecn.status  = 'REJECTED'
        ecn.remarks = request.data.get('reason', '')
        ecn.save(update_fields=['status', 'remarks'])
        return Response(ECNSerializer(ecn, context={'request': request}).data)

# =============================================================================
# FILE: backend/master/views_pl_master.py
# VIEWSET: PLMasterItemViewSet
#   GET    /api/v1/pl-master/             — list (paginated, searchable)
#   POST   /api/v1/pl-master/             — create
#   GET    /api/v1/pl-master/{pl}/        — retrieve
#   PATCH  /api/v1/pl-master/{pl}/        — partial update
#   DELETE /api/v1/pl-master/{pl}/        — soft delete (is_active=False)
#   GET    /api/v1/pl-master/{pl}/bom/    — placeholder BOM tree
# =============================================================================
from rest_framework import viewsets, permissions, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models_pl_master import PLMasterItem
from .serializers_pl_master import PLMasterItemSerializer


class PLMasterItemViewSet(viewsets.ModelViewSet):
    serializer_class   = PLMasterItemSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field       = 'pl_number'
    filter_backends    = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields   = ['inspection_category', 'safety_item', 'is_active']
    search_fields      = ['pl_number', 'description', 'uvam_id', 'application_area']
    ordering_fields    = ['pl_number', 'description', 'inspection_category', 'created_at']
    ordering           = ['pl_number']

    def get_queryset(self):
        qs = PLMasterItem.objects.select_related('created_by', 'updated_by')
        # Support ?q= shorthand used by the frontend
        q = self.request.query_params.get('q', '').strip()
        if q:
            from django.db.models import Q
            qs = qs.filter(
                Q(pl_number__icontains=q) |
                Q(description__icontains=q) |
                Q(uvam_id__icontains=q)
            )
        return qs

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user, updated_by=self.request.user)

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)

    def destroy(self, request, *args, **kwargs):
        """Soft delete — set is_active=False instead of hard delete."""
        obj = self.get_object()
        obj.is_active = False
        obj.updated_by = request.user
        obj.save(update_fields=['is_active', 'updated_by', 'updated_at'])
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['get'], url_path='bom')
    def bom(self, request, pl_number=None):
        """Placeholder BOM tree endpoint."""
        return Response({'pl_number': pl_number, 'bom': [], 'message': 'BOM tree not yet configured.'})

from rest_framework import filters, viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Count

from .models import LocomotiveType, ComponentCatalog, LookupCategory, MasterDataChangeLog
from .serializers import (
    LocomotiveTypeSerializer, ComponentCatalogSerializer,
    LookupCategorySerializer, MasterDataChangeLogSerializer,
)


class LocomotiveTypeViewSet(viewsets.ModelViewSet):
    queryset = LocomotiveType.objects.all()
    serializer_class = LocomotiveTypeSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'engine_type', 'manufacturer']
    search_fields    = ['model_id', 'name', 'loco_class']
    ordering_fields  = ['model_id', 'name', 'status', 'year_introduced']


class ComponentCatalogViewSet(viewsets.ModelViewSet):
    queryset = ComponentCatalog.objects.all()
    serializer_class = ComponentCatalogSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'status', 'supplier']
    search_fields    = ['part_number', 'description']
    ordering_fields  = ['part_number', 'description', 'category']


class LookupCategoryViewSet(viewsets.ModelViewSet):
    queryset = LookupCategory.objects.prefetch_related('items').all()
    serializer_class = LookupCategorySerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter]
    search_fields   = ['name', 'code']


class MasterDataChangeLogViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = MasterDataChangeLog.objects.select_related('user').all()
    serializer_class = MasterDataChangeLogSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['action', 'model_name']
    ordering_fields  = ['timestamp']


class MasterDataSummaryView(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]

    def list(self, request):
        loco_count  = LocomotiveType.objects.count()
        comp_count  = ComponentCatalog.objects.count()
        cat_count   = LookupCategory.objects.count()
        locos       = LocomotiveType.objects.all()[:10]
        updates     = MasterDataChangeLog.objects.select_related('user').all()[:5]
        categories  = LookupCategory.objects.prefetch_related('items').all()[:8]

        return Response({
            'loco_type_count':       loco_count,
            'component_count':       comp_count,
            'lookup_category_count': cat_count,
            'loco_models':           LocomotiveTypeSerializer(locos, many=True).data,
            'recent_updates':        MasterDataChangeLogSerializer(updates, many=True).data,
            'lookup_categories':     LookupCategorySerializer(categories, many=True).data,
        })

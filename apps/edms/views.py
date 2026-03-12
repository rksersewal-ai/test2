"""EDMS API views."""
from rest_framework import viewsets, permissions, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q
from apps.edms.models import Document, Revision, FileAttachment, Category, DocumentType
from apps.edms.serializers import (
    DocumentListSerializer, DocumentDetailSerializer,
    RevisionSerializer, FileAttachmentSerializer,
    CategorySerializer, DocumentTypeSerializer,
)
from apps.core.permissions import IsEngineerOrAbove


class DocumentViewSet(viewsets.ModelViewSet):
    queryset = Document.objects.select_related('category', 'section', 'document_type', 'created_by').all()
    permission_classes = [permissions.IsAuthenticated, IsEngineerOrAbove]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'category', 'section', 'document_type', 'source_standard']
    search_fields = ['document_number', 'title', 'keywords', 'eoffice_file_number']
    ordering_fields = ['document_number', 'created_at', 'updated_at']
    ordering = ['document_number']

    def get_serializer_class(self):
        if self.action in ('retrieve', 'create', 'update', 'partial_update'):
            return DocumentDetailSerializer
        return DocumentListSerializer

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    @action(detail=False, methods=['get'], url_path='search')
    def search(self, request):
        q = request.query_params.get('q', '').strip()
        if not q:
            return Response({'error': 'Query parameter q is required.'}, status=status.HTTP_400_BAD_REQUEST)
        qs = self.queryset.filter(
            Q(document_number__icontains=q) |
            Q(title__icontains=q) |
            Q(keywords__icontains=q) |
            Q(eoffice_file_number__icontains=q) |
            Q(revisions__files__ocr_result__full_text__icontains=q)
        ).distinct()
        serializer = DocumentListSerializer(qs, many=True)
        return Response(serializer.data)


class RevisionViewSet(viewsets.ModelViewSet):
    queryset = Revision.objects.select_related('document', 'created_by').prefetch_related('files').all()
    serializer_class = RevisionSerializer
    permission_classes = [permissions.IsAuthenticated, IsEngineerOrAbove]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['document', 'status']
    ordering_fields = ['created_at', 'revision_date']
    ordering = ['-created_at']

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.filter(is_active=True).all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticated]


class DocumentTypeViewSet(viewsets.ModelViewSet):
    queryset = DocumentType.objects.filter(is_active=True).all()
    serializer_class = DocumentTypeSerializer
    permission_classes = [permissions.IsAuthenticated]

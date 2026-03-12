"""EDMS API views — refactored to use repository + service layers."""
from rest_framework import viewsets, permissions, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from apps.edms.models import Document, Revision, FileAttachment, Category, DocumentType
from apps.edms.serializers import (
    DocumentListSerializer, DocumentDetailSerializer,
    RevisionSerializer, FileAttachmentSerializer,
    CategorySerializer, DocumentTypeSerializer,
)
from apps.edms.filters import DocumentFilter, RevisionFilter, FileAttachmentFilter
from apps.edms.repository import DocumentRepository, RevisionRepository
from apps.edms.services import DocumentService, RevisionService
from apps.core.permissions import IsEngineerOrAbove


class DocumentViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated, IsEngineerOrAbove]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = DocumentFilter
    search_fields = ['document_number', 'title', 'keywords', 'eoffice_file_number']
    ordering_fields = ['document_number', 'created_at', 'updated_at']
    ordering = ['document_number']

    def get_queryset(self):
        if self.action == 'retrieve':
            return DocumentRepository.get_detail_qs()
        return DocumentRepository.get_list_qs()

    def get_serializer_class(self):
        if self.action in ('retrieve', 'create', 'update', 'partial_update'):
            return DocumentDetailSerializer
        return DocumentListSerializer

    def perform_create(self, serializer):
        data = {k: v for k, v in serializer.validated_data.items()}
        DocumentService.create_document(data, created_by=self.request.user)

    @action(detail=False, methods=['get'], url_path='search')
    def search(self, request):
        q = request.query_params.get('q', '').strip()
        if not q:
            return Response(
                {'error': 'Query parameter q is required.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        qs = DocumentRepository.fulltext_search(q)
        page = self.paginate_queryset(qs)
        if page is not None:
            return self.get_paginated_response(DocumentListSerializer(page, many=True).data)
        return Response(DocumentListSerializer(qs, many=True).data)

    @action(detail=True, methods=['post'], url_path='change-status')
    def change_status(self, request, pk=None):
        doc = self.get_object()
        new_status = request.data.get('status')
        if new_status not in Document.Status.values:
            return Response(
                {'error': f'Invalid status. Choices: {Document.Status.values}'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        DocumentService.update_status(doc, new_status, request.user)
        return Response({'status': new_status})


class RevisionViewSet(viewsets.ModelViewSet):
    serializer_class = RevisionSerializer
    permission_classes = [permissions.IsAuthenticated, IsEngineerOrAbove]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_class = RevisionFilter
    ordering_fields = ['created_at', 'revision_date']
    ordering = ['-created_at']

    def get_queryset(self):
        return RevisionRepository.get_list_qs()

    def perform_create(self, serializer):
        document = serializer.validated_data['document']
        data = {k: v for k, v in serializer.validated_data.items() if k != 'document'}
        RevisionService.create_revision(document, data, created_by=self.request.user)


class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Category.objects.filter(is_active=True)
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticated]


class DocumentTypeViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = DocumentType.objects.filter(is_active=True)
    serializer_class = DocumentTypeSerializer
    permission_classes = [permissions.IsAuthenticated]

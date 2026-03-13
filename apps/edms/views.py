# =============================================================================
# FILE: apps/edms/views.py
# SPRINT 1 additions:
#   - DocumentViewSet.custom_fields()        GET/POST  (Feature #9)
#   - DocumentViewSet.bulk_update()          POST      (Feature #6 placeholder)
#   - CustomFieldDefinitionViewSet           CRUD      (Feature #9, admin)
#   - DocumentCustomFieldViewSet             CRUD      (Feature #9)
#   - CorrespondentViewSet                   CRUD      (Feature #14)
#   - DocumentCorrespondentLinkViewSet       CRUD      (Feature #14)
#   - DocumentNoteViewSet                    list/create/resolve (Feature #12)
# All existing ViewSets (Document, Revision, Category, DocumentType) unchanged.
# =============================================================================
from django.utils import timezone
from django.db import transaction
from rest_framework import viewsets, permissions, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend

from apps.edms.models import (
    Document, Revision, FileAttachment, Category, DocumentType,
    CustomFieldDefinition, DocumentCustomField,
    Correspondent, DocumentCorrespondentLink,
    DocumentNote,
)
from apps.edms.serializers import (
    DocumentListSerializer, DocumentDetailSerializer,
    RevisionSerializer, FileAttachmentSerializer,
    CategorySerializer, DocumentTypeSerializer,
    CustomFieldDefinitionSerializer, DocumentCustomFieldSerializer,
    BulkUpsertCustomFieldsSerializer,
    CorrespondentSerializer, DocumentCorrespondentLinkSerializer,
    DocumentNoteSerializer, ResolveNoteSerializer,
)
from apps.edms.filters import DocumentFilter, RevisionFilter, FileAttachmentFilter
from apps.edms.repository import DocumentRepository, RevisionRepository
from apps.edms.services import DocumentService, RevisionService
from apps.core.permissions import IsEngineerOrAbove, IsAdminOrSectionHead, CanManageDropdowns


# ---------------------------------------------------------------------------
# Existing ViewSets (with Sprint 1 actions added)
# ---------------------------------------------------------------------------

class DocumentViewSet(viewsets.ModelViewSet):
    permission_classes  = [permissions.IsAuthenticated, IsEngineerOrAbove]
    filter_backends     = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class     = DocumentFilter
    search_fields       = ['document_number', 'title', 'keywords', 'eoffice_file_number']
    ordering_fields     = ['document_number', 'created_at', 'updated_at']
    ordering            = ['document_number']

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
            return Response({'error': 'Query parameter q is required.'},
                            status=status.HTTP_400_BAD_REQUEST)
        qs   = DocumentRepository.fulltext_search(q)
        page = self.paginate_queryset(qs)
        if page is not None:
            return self.get_paginated_response(DocumentListSerializer(page, many=True).data)
        return Response(DocumentListSerializer(qs, many=True).data)

    @action(detail=True, methods=['post'], url_path='change-status')
    def change_status(self, request, pk=None):
        doc        = self.get_object()
        new_status = request.data.get('status')
        if new_status not in Document.Status.values:
            return Response({'error': f'Invalid status. Choices: {Document.Status.values}'},
                            status=status.HTTP_400_BAD_REQUEST)
        DocumentService.update_status(doc, new_status, request.user)
        return Response({'status': new_status})

    # ---- Sprint 1: Feature #9 — Custom Fields ----

    @action(detail=True, methods=['get', 'post'], url_path='custom-fields')
    def custom_fields(self, request, pk=None):
        doc = self.get_object()

        if request.method == 'GET':
            values = DocumentCustomField.objects.filter(document=doc)\
                        .select_related('definition').order_by('definition__sort_order')
            return Response(DocumentCustomFieldSerializer(values, many=True).data)

        # POST: bulk upsert all custom fields for this document in one call
        serializer = BulkUpsertCustomFieldsSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        with transaction.atomic():
            results = []
            for item in serializer.validated_data['fields']:
                def_id      = int(item['definition_id'])
                field_value = item.get('field_value', '')
                try:
                    definition = CustomFieldDefinition.objects.get(
                        pk=def_id, document_type=doc.document_type, is_active=True
                    )
                except CustomFieldDefinition.DoesNotExist:
                    return Response(
                        {'error': f'Definition {def_id} not valid for this document type.'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                obj, _ = DocumentCustomField.objects.update_or_create(
                    document=doc, definition=definition,
                    defaults={'field_value': field_value, 'updated_by': request.user}
                )
                results.append(obj)
        return Response(DocumentCustomFieldSerializer(results, many=True).data,
                        status=status.HTTP_200_OK)

    # ---- Sprint 1: Feature #6 placeholder — Bulk Update ----

    @action(detail=False, methods=['post'], url_path='bulk-update',
            permission_classes=[permissions.IsAuthenticated, IsAdminOrSectionHead])
    def bulk_update(self, request):
        """Bulk-update status / section / document_type for a list of document IDs.
        Accepts: {ids: [1,2,3], fields: {status: 'ACTIVE', section_id: 5}}
        """
        ids    = request.data.get('ids', [])
        fields = request.data.get('fields', {})
        if not ids or not isinstance(ids, list):
            return Response({'error': 'ids must be a non-empty list.'},
                            status=status.HTTP_400_BAD_REQUEST)
        allowed_fields = {'status', 'section_id', 'document_type_id', 'category_id'}
        update_data    = {k: v for k, v in fields.items() if k in allowed_fields}
        if not update_data:
            return Response({'error': f'No valid fields. Allowed: {allowed_fields}'},
                            status=status.HTTP_400_BAD_REQUEST)
        updated = Document.objects.filter(pk__in=ids).update(**update_data)
        return Response({'updated': updated})


class RevisionViewSet(viewsets.ModelViewSet):
    serializer_class   = RevisionSerializer
    permission_classes = [permissions.IsAuthenticated, IsEngineerOrAbove]
    filter_backends    = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_class    = RevisionFilter
    ordering_fields    = ['created_at', 'revision_date']
    ordering           = ['-created_at']

    def get_queryset(self):
        return RevisionRepository.get_list_qs()

    def perform_create(self, serializer):
        document = serializer.validated_data['document']
        data     = {k: v for k, v in serializer.validated_data.items() if k != 'document'}
        RevisionService.create_revision(document, data, created_by=self.request.user)


class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset           = Category.objects.filter(is_active=True)
    serializer_class   = CategorySerializer
    permission_classes = [permissions.IsAuthenticated]


class DocumentTypeViewSet(viewsets.ReadOnlyModelViewSet):
    queryset           = DocumentType.objects.filter(is_active=True)
    serializer_class   = DocumentTypeSerializer
    permission_classes = [permissions.IsAuthenticated]


# ---------------------------------------------------------------------------
# SPRINT 1 — Feature #9: Custom Field Definition admin ViewSet
# ---------------------------------------------------------------------------

class CustomFieldDefinitionViewSet(viewsets.ModelViewSet):
    """Admin-only CRUD for defining custom fields per document type."""
    serializer_class   = CustomFieldDefinitionSerializer
    permission_classes = [permissions.IsAuthenticated, CanManageDropdowns]
    filter_backends    = [DjangoFilterBackend]

    def get_queryset(self):
        qs = CustomFieldDefinition.objects.select_related('document_type')
        doc_type = self.request.query_params.get('document_type')
        if doc_type:
            qs = qs.filter(document_type_id=doc_type)
        return qs.order_by('document_type', 'sort_order')


# ---------------------------------------------------------------------------
# SPRINT 1 — Feature #14: Correspondent ViewSets
# ---------------------------------------------------------------------------

class CorrespondentViewSet(viewsets.ModelViewSet):
    serializer_class   = CorrespondentSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends    = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields      = ['name', 'short_code']
    ordering_fields    = ['name', 'org_type']
    ordering           = ['name']

    def get_queryset(self):
        qs = Correspondent.objects.all()
        org_type = self.request.query_params.get('org_type')
        if org_type:
            qs = qs.filter(org_type=org_type)
        active = self.request.query_params.get('active', 'true')
        if active.lower() == 'true':
            qs = qs.filter(is_active=True)
        return qs

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class DocumentCorrespondentLinkViewSet(viewsets.ModelViewSet):
    serializer_class   = DocumentCorrespondentLinkSerializer
    permission_classes = [permissions.IsAuthenticated, IsEngineerOrAbove]
    filter_backends    = [DjangoFilterBackend]

    def get_queryset(self):
        qs = DocumentCorrespondentLink.objects.select_related('correspondent', 'created_by')
        doc = self.request.query_params.get('document')
        if doc:
            qs = qs.filter(document_id=doc)
        return qs.order_by('-created_at')

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


# ---------------------------------------------------------------------------
# SPRINT 1 — Feature #12: Document Notes ViewSet
# ---------------------------------------------------------------------------

class DocumentNoteViewSet(viewsets.GenericViewSet,
                          viewsets.mixins.ListModelMixin,
                          viewsets.mixins.CreateModelMixin,
                          viewsets.mixins.RetrieveModelMixin):
    """Notes are append-only. No update, no delete (audit safety).
    Use POST .../resolve/ to mark a note as resolved.
    """
    serializer_class   = DocumentNoteSerializer
    permission_classes = [permissions.IsAuthenticated, IsEngineerOrAbove]
    filter_backends    = [DjangoFilterBackend, filters.OrderingFilter]
    ordering           = ['-created_at']

    def get_queryset(self):
        qs  = DocumentNote.objects.select_related(
            'created_by', 'resolved_by', 'document', 'revision'
        )
        doc = self.request.query_params.get('document')
        rev = self.request.query_params.get('revision')
        if doc:
            qs = qs.filter(document_id=doc)
        if rev:
            qs = qs.filter(revision_id=rev)
        unresolved = self.request.query_params.get('unresolved')
        if unresolved == 'true':
            qs = qs.filter(is_resolved=False)
        return qs

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    @action(detail=True, methods=['patch'], url_path='resolve',
            permission_classes=[permissions.IsAuthenticated, IsEngineerOrAbove])
    def resolve(self, request, pk=None):
        note = self.get_object()
        if note.is_resolved:
            return Response({'detail': 'Note is already resolved.'},
                            status=status.HTTP_400_BAD_REQUEST)
        serializer = ResolveNoteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        note.is_resolved     = True
        note.resolved_by     = request.user
        note.resolved_at     = timezone.now()
        note.resolution_note = serializer.validated_data.get('resolution_note', '')
        note.save(update_fields=['is_resolved', 'resolved_by', 'resolved_at',
                                 'resolution_note', 'updated_at'])
        return Response(DocumentNoteSerializer(note).data)

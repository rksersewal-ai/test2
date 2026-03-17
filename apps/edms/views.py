# =============================================================================
# FILE: apps/edms/views.py
# SPRINT 2 addition:
#   - DocumentViewSet.similar_documents()  GET  (Feature #8)
# All Sprint 1 additions and existing ViewSets preserved exactly.
# =============================================================================
from django.utils import timezone
from django.db import transaction
from django.http import FileResponse, Http404
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
        serializer.instance = DocumentService.create_document(data, created_by=self.request.user)

    def _latest_attachment(self, document):
        revision = (
            document.revisions
            .prefetch_related('files')
            .order_by('-revision_date', '-created_at')
            .first()
        )
        if revision is None:
            raise Http404('No revision found for this document.')

        attachment = revision.files.order_by('-is_primary', '-uploaded_at').first()
        if attachment is None:
            raise Http404('No file attached to this document.')
        return attachment

    # ---- Existing actions ----

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

    @action(detail=True, methods=['post'], url_path='approve')
    def approve(self, request, pk=None):
        doc = self.get_object()
        DocumentService.update_status(doc, Document.Status.ACTIVE, request.user)
        doc.refresh_from_db()
        return Response(DocumentDetailSerializer(doc, context={'request': request}).data)

    @action(detail=True, methods=['post'], url_path='reject')
    def reject(self, request, pk=None):
        doc = self.get_object()
        DocumentService.update_status(doc, Document.Status.DRAFT, request.user)
        doc.refresh_from_db()
        return Response(DocumentDetailSerializer(doc, context={'request': request}).data)

    @action(detail=True, methods=['get'], url_path='versions')
    def versions(self, request, pk=None):
        doc = self.get_object()
        revisions = doc.revisions.order_by('-revision_date', '-created_at')
        page = self.paginate_queryset(revisions)
        serializer = RevisionSerializer(page or revisions, many=True, context={'request': request})
        if page is not None:
            return self.get_paginated_response(serializer.data)
        return Response(serializer.data)

    @action(detail=True, methods=['get'], url_path='download')
    def download(self, request, pk=None):
        doc = self.get_object()
        attachment = self._latest_attachment(doc)
        response = FileResponse(attachment.file_path.open('rb'), as_attachment=True, filename=attachment.file_name)
        return response

    @action(detail=True, methods=['get'], url_path='file')
    def file(self, request, pk=None):
        doc = self.get_object()
        attachment = self._latest_attachment(doc)
        return FileResponse(attachment.file_path.open('rb'), filename=attachment.file_name)

    @action(detail=True, methods=['get'], url_path='related')
    def related(self, request, pk=None):
        doc = self.get_object()
        related_qs = (
            Document.objects
            .select_related('document_type')
            .filter(
                Q(category=doc.category) | Q(document_type=doc.document_type)
            )
            .exclude(pk=doc.pk)
            .order_by('document_number')[:10]
        )
        payload = [
            {
                'id': related.pk,
                'doc_number': related.document_number,
                'title': related.title,
                'doc_type': related.document_type.name if related.document_type else '',
                'status': related.status,
                'relation_type': 'LINKED',
            }
            for related in related_qs
        ]
        return Response(payload)

    # ---- Sprint 1: Feature #9 — Custom Fields ----

    @action(detail=True, methods=['get', 'post'], url_path='custom-fields')
    def custom_fields(self, request, pk=None):
        doc = self.get_object()
        if request.method == 'GET':
            values = DocumentCustomField.objects.filter(document=doc)\
                        .select_related('definition').order_by('definition__sort_order')
            return Response(DocumentCustomFieldSerializer(values, many=True).data)
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
        return Response(DocumentCustomFieldSerializer(results, many=True).data)

    # ---- Sprint 1: Feature #6 placeholder — Bulk Update ----

    @action(detail=False, methods=['post'], url_path='bulk-update',
            permission_classes=[permissions.IsAuthenticated, IsAdminOrSectionHead])
    def bulk_update(self, request):
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

    # ---- Sprint 2: Feature #8 — Similarity Search ----

    @action(detail=True, methods=['get'], url_path='similar')
    def similar_documents(self, request, pk=None):
        """
        GET /api/edms/documents/{id}/similar/
        Optional query params:
          ?limit=10          max results (default 10, max 25)
          ?threshold=0.08    similarity score floor (0.0 – 1.0)
        """
        doc = self.get_object()  # ensures 404 + permission check

        try:
            limit = min(int(request.query_params.get('limit', 10)), 25)
        except (TypeError, ValueError):
            limit = 10

        try:
            threshold = float(request.query_params.get('threshold',
                                DocumentRepository.SIMILARITY_THRESHOLD))
            threshold = max(0.01, min(threshold, 0.99))
        except (TypeError, ValueError):
            threshold = DocumentRepository.SIMILARITY_THRESHOLD

        results = DocumentRepository.get_similar_documents(
            document_id=doc.pk,
            limit=limit,
            threshold=threshold,
        )
        return Response({
            'source_id':   doc.pk,
            'source_title': doc.title,
            'count':       len(results),
            'results':     results,
        })


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
        serializer.instance = RevisionService.create_revision(document, data, created_by=self.request.user)


class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset           = Category.objects.filter(is_active=True)
    serializer_class   = CategorySerializer
    permission_classes = [permissions.IsAuthenticated]


class DocumentTypeViewSet(viewsets.ReadOnlyModelViewSet):
    queryset           = DocumentType.objects.filter(is_active=True)
    serializer_class   = DocumentTypeSerializer
    permission_classes = [permissions.IsAuthenticated]


# ---------------------------------------------------------------------------
# Sprint 1 — Feature #9: Custom Field Definition admin ViewSet
# ---------------------------------------------------------------------------

class CustomFieldDefinitionViewSet(viewsets.ModelViewSet):
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
# Sprint 1 — Feature #14: Correspondent ViewSets
# ---------------------------------------------------------------------------

class CorrespondentViewSet(viewsets.ModelViewSet):
    serializer_class   = CorrespondentSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends    = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields      = ['name', 'short_code']
    ordering_fields    = ['name', 'org_type']
    ordering           = ['name']

    def get_queryset(self):
        qs       = Correspondent.objects.all()
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
        qs  = DocumentCorrespondentLink.objects.select_related('correspondent', 'created_by')
        doc = self.request.query_params.get('document')
        if doc:
            qs = qs.filter(document_id=doc)
        return qs.order_by('-created_at')

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


# ---------------------------------------------------------------------------
# Sprint 1 — Feature #12: Document Notes ViewSet
# ---------------------------------------------------------------------------

class DocumentNoteViewSet(viewsets.GenericViewSet,
                          viewsets.mixins.ListModelMixin,
                          viewsets.mixins.CreateModelMixin,
                          viewsets.mixins.RetrieveModelMixin):
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
        if self.request.query_params.get('unresolved') == 'true':
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

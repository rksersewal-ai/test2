from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import RetentionPolicy, DocumentLifecycle, LifecycleEvent
from .serializers import RetentionPolicySerializer, DocumentLifecycleSerializer, LifecycleEventSerializer
from .services import LifecycleService
from apps.edms.models import Document


class RetentionPolicyViewSet(viewsets.ModelViewSet):
    queryset           = RetentionPolicy.objects.filter(is_active=True)
    serializer_class   = RetentionPolicySerializer
    permission_classes = [IsAuthenticated]


class DocumentLifecycleViewSet(viewsets.ModelViewSet):
    queryset           = DocumentLifecycle.objects.select_related('document', 'policy')
    serializer_class   = DocumentLifecycleSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        qs     = super().get_queryset()
        state  = self.request.query_params.get('state')
        doc_id = self.request.query_params.get('document')
        if state:
            qs = qs.filter(state=state)
        if doc_id:
            qs = qs.filter(document_id=doc_id)
        return qs

    @action(detail=False, methods=['post'], url_path='legal-hold')
    def legal_hold(self, request):
        doc_id = request.data.get('document')
        reason = request.data.get('reason', '')
        try:
            doc = Document.objects.get(pk=doc_id)
            lc  = LifecycleService.place_legal_hold(doc, reason, user=request.user)
        except Document.DoesNotExist:
            return Response({'error': 'Document not found'}, status=status.HTTP_404_NOT_FOUND)
        return Response(DocumentLifecycleSerializer(lc).data)

    @action(detail=False, methods=['post'], url_path='release-hold')
    def release_hold(self, request):
        doc_id = request.data.get('document')
        try:
            doc = Document.objects.get(pk=doc_id)
            lc  = LifecycleService.release_legal_hold(doc, user=request.user)
        except Document.DoesNotExist:
            return Response({'error': 'Document not found'}, status=status.HTTP_404_NOT_FOUND)
        return Response(DocumentLifecycleSerializer(lc).data)

    @action(detail=False, methods=['post'], url_path='archive')
    def archive(self, request):
        doc_id = request.data.get('document')
        reason = request.data.get('reason', '')
        try:
            doc = Document.objects.get(pk=doc_id)
            lc  = LifecycleService.archive(doc, user=request.user, reason=reason)
        except Document.DoesNotExist:
            return Response({'error': 'Document not found'}, status=status.HTTP_404_NOT_FOUND)
        return Response(DocumentLifecycleSerializer(lc).data)

    @action(detail=False, methods=['post'], url_path='schedule-deletion')
    def schedule_deletion(self, request):
        doc_id = request.data.get('document')
        reason = request.data.get('reason', '')
        try:
            doc = Document.objects.get(pk=doc_id)
            lc  = LifecycleService.schedule_deletion(doc, user=request.user, reason=reason)
        except Document.DoesNotExist:
            return Response({'error': 'Document not found'}, status=status.HTTP_404_NOT_FOUND)
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(DocumentLifecycleSerializer(lc).data)


class LifecycleEventViewSet(viewsets.ReadOnlyModelViewSet):
    queryset           = LifecycleEvent.objects.select_related('document', 'triggered_by')
    serializer_class   = LifecycleEventSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        qs     = super().get_queryset()
        doc_id = self.request.query_params.get('document')
        if doc_id:
            qs = qs.filter(document_id=doc_id)
        return qs

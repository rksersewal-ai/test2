# =============================================================================
# FILE: apps/ml_classifier/views.py
# SPRINT 5 — ML Classifier REST endpoints
#
# GET  /api/ml/models/                        — list trained classifier versions
# POST /api/ml/train/                         — trigger full retrain (admin only)
# POST /api/ml/classify/{document_id}/        — classify one document, save results
# GET  /api/ml/results/?document={id}         — list ClassificationResults
# POST /api/ml/results/{id}/accept/           — accept top prediction, apply to doc
# POST /api/ml/results/{id}/override/         — override with chosen label_id
# POST /api/ml/results/{id}/reject/           — reject prediction (keep existing)
# =============================================================================
from django.utils import timezone
from django.shortcuts import get_object_or_404
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.ml_classifier.models      import ClassifierModel, ClassificationResult
from apps.ml_classifier.serializers import (
    ClassifierModelSerializer, ClassificationResultSerializer,
    AcceptPredictionSerializer,
)
from apps.core.permissions import IsAdminOrSectionHead, IsEngineerOrAbove


class ClassifierModelViewSet(viewsets.ReadOnlyModelViewSet):
    """
    GET /api/ml/models/       — list all trained model versions
    POST /api/ml/models/train/— retrain all classifiers (admin only)
    """
    queryset           = ClassifierModel.objects.all().select_related('trained_by')
    serializer_class   = ClassifierModelSerializer
    permission_classes = [permissions.IsAuthenticated]

    @action(
        detail=False, methods=['post'], url_path='train',
        permission_classes=[permissions.IsAuthenticated, IsAdminOrSectionHead]
    )
    def train(self, request):
        """
        Enqueue a full retrain via Celery so the HTTP request returns immediately.
        Returns task_id for polling.
        """
        try:
            from apps.ml_classifier.tasks import retrain_all_classifiers
            task = retrain_all_classifiers.delay(user_id=request.user.pk)
            return Response(
                {'status': 'queued', 'task_id': task.id},
                status=status.HTTP_202_ACCEPTED
            )
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ClassificationResultViewSet(viewsets.GenericViewSet,
                                   viewsets.mixins.ListModelMixin,
                                   viewsets.mixins.RetrieveModelMixin):
    """
    Exposes classification results with accept / override / reject actions.
    """
    serializer_class   = ClassificationResultSerializer
    permission_classes = [permissions.IsAuthenticated, IsEngineerOrAbove]

    def get_queryset(self):
        qs = ClassificationResult.objects.select_related(
            'document', 'classifier', 'reviewed_by'
        )
        doc = self.request.query_params.get('document')
        if doc:
            qs = qs.filter(document_id=doc)
        outcome = self.request.query_params.get('outcome')
        if outcome:
            qs = qs.filter(outcome=outcome)
        return qs

    # ---- classify a document on-demand ------------------------------------

    @action(detail=False, methods=['post'], url_path=r'classify/(?P<document_id>[0-9]+)')
    def classify(self, request, document_id=None):
        """POST /api/ml/results/classify/{document_id}/"""
        from apps.ml_classifier.inference import classify_and_save
        predictions = classify_and_save(int(document_id))
        if not predictions:
            return Response(
                {'error': f'Document #{document_id} not found or no text available.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        return Response(predictions)

    # ---- accept top prediction & apply to doc -----------------------------

    @action(detail=True, methods=['post'], url_path='accept')
    def accept(self, request, pk=None):
        result = self.get_object()
        if result.outcome != ClassificationResult.Outcome.PENDING:
            return Response({'error': 'Already reviewed.'}, status=status.HTTP_400_BAD_REQUEST)

        self._apply_to_document(result, result.top_label)
        result.outcome     = ClassificationResult.Outcome.ACCEPTED
        result.reviewed_by = request.user
        result.reviewed_at = timezone.now()
        result.save(update_fields=['outcome', 'reviewed_by', 'reviewed_at'])
        return Response(ClassificationResultSerializer(result).data)

    # ---- override with a different label from the top-3 list --------------

    @action(detail=True, methods=['post'], url_path='override')
    def override(self, request, pk=None):
        result = self.get_object()
        ser = AcceptPredictionSerializer(data=request.data)
        ser.is_valid(raise_exception=True)

        chosen_id = ser.validated_data.get('accepted_label_id')
        pred_match = next(
            (p for p in result.predictions if p['label_id'] == chosen_id), None
        )
        if not pred_match:
            return Response(
                {'error': f'label_id {chosen_id} not in prediction list.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        self._apply_to_document(result, pred_match['label'], label_id=chosen_id)
        result.outcome     = ClassificationResult.Outcome.OVERRIDDEN
        result.reviewed_by = request.user
        result.reviewed_at = timezone.now()
        result.save(update_fields=['outcome', 'reviewed_by', 'reviewed_at'])
        return Response(ClassificationResultSerializer(result).data)

    # ---- reject (keep existing metadata) ----------------------------------

    @action(detail=True, methods=['post'], url_path='reject')
    def reject(self, request, pk=None):
        result = self.get_object()
        result.outcome     = ClassificationResult.Outcome.REJECTED
        result.reviewed_by = request.user
        result.reviewed_at = timezone.now()
        result.save(update_fields=['outcome', 'reviewed_by', 'reviewed_at'])
        return Response(ClassificationResultSerializer(result).data)

    # ---- helper -----------------------------------------------------------

    @staticmethod
    def _apply_to_document(result: ClassificationResult, label: str, label_id: int = None):
        """
        Apply a predicted label to the document FK field.
        Handles document_type and category lookups by name.
        Correspondent assignment is informational only (not auto-applied).
        """
        doc = result.document
        if result.target == 'document_type':
            from apps.edms.models import DocumentType
            dt = DocumentType.objects.filter(name=label).first()
            if dt:
                doc.document_type = dt
                doc.save(update_fields=['document_type', 'updated_at'])
        elif result.target == 'category':
            from apps.edms.models import Category
            cat = Category.objects.filter(name=label).first()
            if cat:
                doc.category = cat
                doc.save(update_fields=['category', 'updated_at'])
        # correspondent: shown as suggestion only, user manually confirms

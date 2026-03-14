# =============================================================================
# FILE: backend/master/views_pl_docs.py
# VIEWS for VD/NVD vendor info and PL linked documents
#
# Routes (all under /api/v1/pl-master/{pl_number}/):
#   GET/PUT/PATCH  vendor-info/
#   GET            linked-docs/           (all, grouped by category)
#   POST           linked-docs/           (link a document)
#   DELETE         linked-docs/{id}/      (unlink)
#   GET            linked-docs/search/    (search EDMS docs to link)
# =============================================================================
import logging
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from django.shortcuts import get_object_or_404
from django.db.models import Q
from .models_pl_docs import PLVendorInfo, PLLinkedDocument, DOC_CATEGORY_CHOICES
from .serializers_pl_docs import PLVendorInfoSerializer, PLLinkedDocumentSerializer

logger = logging.getLogger('edms.pl_docs')


# ─────────────────────────────────────────────────────────────────────────────
# Vendor Info
# ─────────────────────────────────────────────────────────────────────────────
class PLVendorInfoView(APIView):
    """
    GET   /pl-master/{pl_number}/vendor-info/  — retrieve or create default
    PUT   /pl-master/{pl_number}/vendor-info/  — full update
    PATCH /pl-master/{pl_number}/vendor-info/  — partial update
    """
    permission_classes = [permissions.IsAuthenticated]

    def _get_or_create(self, pl_number):
        obj, _ = PLVendorInfo.objects.get_or_create(
            pl_number=pl_number,
            defaults={'vendor_type': 'NVD'}
        )
        return obj

    def get(self, request, pl_number):
        obj = self._get_or_create(pl_number)
        return Response(PLVendorInfoSerializer(obj).data)

    def put(self, request, pl_number):
        return self._save(request, pl_number, partial=False)

    def patch(self, request, pl_number):
        return self._save(request, pl_number, partial=True)

    def _save(self, request, pl_number, partial):
        obj = self._get_or_create(pl_number)
        ser = PLVendorInfoSerializer(obj, data=request.data, partial=partial)
        if not ser.is_valid():
            return Response(ser.errors, status=status.HTTP_400_BAD_REQUEST)
        ser.save(updated_by=request.user)
        return Response(ser.data)


# ─────────────────────────────────────────────────────────────────────────────
# Linked Documents
# ─────────────────────────────────────────────────────────────────────────────
class PLLinkedDocListView(APIView):
    """
    GET  /pl-master/{pl_number}/linked-docs/
    POST /pl-master/{pl_number}/linked-docs/
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pl_number):
        qs    = PLLinkedDocument.objects.filter(pl_number=pl_number).select_related('linked_by')
        q     = request.query_params.get('q', '').strip()
        cat   = request.query_params.get('category', '').strip()
        if q:
            qs = qs.filter(
                Q(document_title__icontains=q) |
                Q(document_number__icontains=q) |
                Q(remarks__icontains=q)
            )
        if cat:
            qs = qs.filter(category=cat)

        # Group by category for accordion
        grouped: dict = {c[0]: [] for c in DOC_CATEGORY_CHOICES}
        for doc in qs:
            ser = PLLinkedDocumentSerializer(doc)
            grouped[doc.category].append(ser.data)

        return Response({
            'total' : qs.count(),
            'grouped': grouped,
            'results': PLLinkedDocumentSerializer(qs, many=True).data,
        })

    def post(self, request, pl_number):
        # Hard limit
        if PLLinkedDocument.objects.filter(pl_number=pl_number).count() >= 100:
            return Response(
                {'detail': 'Maximum 100 documents can be linked to one PL number.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        data = {**request.data, 'pl_number': pl_number}
        ser  = PLLinkedDocumentSerializer(data=data)
        if not ser.is_valid():
            return Response(ser.errors, status=status.HTTP_400_BAD_REQUEST)
        ser.save(linked_by=request.user)
        logger.info('Linked doc %s to PL %s by %s', data.get('document_id'), pl_number, request.user)
        return Response(ser.data, status=status.HTTP_201_CREATED)


class PLLinkedDocDetailView(APIView):
    """
    DELETE /pl-master/{pl_number}/linked-docs/{pk}/
    """
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request, pl_number, pk):
        doc = get_object_or_404(PLLinkedDocument, pk=pk, pl_number=pl_number)
        doc.delete()
        logger.info('Unlinked doc %s from PL %s by %s', pk, pl_number, request.user)
        return Response(status=status.HTTP_204_NO_CONTENT)


class PLDocSearchView(APIView):
    """
    GET /pl-master/{pl_number}/linked-docs/search/?q=...
    Searches the EDMS Document table to find documents to link.
    Returns top 20 matches excluding already-linked ones.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pl_number):
        q = request.query_params.get('q', '').strip()
        if len(q) < 2:
            return Response({'results': []})

        # Import Document model lazily to avoid circular imports
        try:
            from django.apps import apps
            Document = apps.get_model('documents', 'Document')
        except LookupError:
            # Fallback: try common app names
            try:
                from django.apps import apps
                Document = apps.get_model('edms_docs', 'Document')
            except LookupError:
                return Response({'results': [], 'detail': 'Document model not found.'}, status=200)

        already_linked = set(
            PLLinkedDocument.objects.filter(pl_number=pl_number)
            .values_list('document_id', flat=True)
        )
        docs = (
            Document.objects
            .filter(Q(title__icontains=q) | Q(document_number__icontains=q))
            .exclude(id__in=already_linked)
            .values('id', 'title', 'document_number', 'document_type')[:20]
        )
        return Response({'results': list(docs)})

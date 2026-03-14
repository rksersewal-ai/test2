# =============================================================================
# FILE: backend/master/views_tech_eval.py
# VIEWS: PLTechEvalDocumentView
#
# GET  /pl-master/{pl_number}/tech-eval-docs/  — list docs for a PL
# POST /pl-master/{pl_number}/tech-eval-docs/  — upload a new doc
# DELETE /pl-master/{pl_number}/tech-eval-docs/{pk}/ — remove a doc
# =============================================================================
import logging
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework import status, permissions
from django.shortcuts import get_object_or_404
from django.core.exceptions import ValidationError as DjangoValidationError
from .models_tech_eval import PLTechEvalDocument
from .serializers_tech_eval import (
    PLTechEvalDocumentSerializer,
    PLTechEvalDocumentUploadSerializer,
)

logger = logging.getLogger('edms.pl_tech_eval')


class PLTechEvalDocListView(APIView):
    """
    GET  /pl-master/{pl_number}/tech-eval-docs/
    POST /pl-master/{pl_number}/tech-eval-docs/
    """
    parser_classes     = [MultiPartParser, FormParser]
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pl_number):
        docs = (
            PLTechEvalDocument.objects
            .filter(pl_number=pl_number)
            .select_related('uploaded_by')
            .order_by('-uploaded_at')[:3]       # never return more than 3
        )
        serializer = PLTechEvalDocumentSerializer(
            docs, many=True, context={'request': request}
        )
        return Response({'count': len(serializer.data), 'results': serializer.data})

    def post(self, request, pl_number):
        # Check limit before doing any I/O
        existing_count = PLTechEvalDocument.objects.filter(pl_number=pl_number).count()
        if existing_count >= 3:
            return Response(
                {'detail': 'Maximum 3 technical evaluation documents allowed per PL. '
                           'Delete an existing document before uploading.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        upload_ser = PLTechEvalDocumentUploadSerializer(data=request.data)
        if not upload_ser.is_valid():
            return Response(upload_ser.errors, status=status.HTTP_400_BAD_REQUEST)

        vd = upload_ser.validated_data
        try:
            doc = PLTechEvalDocument(
                pl_number    = pl_number,
                tender_number= vd['tender_number'],
                eval_year    = vd['eval_year'],
                document_file= vd['file'],
                uploaded_by  = request.user,
            )
            doc.full_clean(exclude=['file_name', 'file_format', 'file_size_kb'])
            doc.save()
        except DjangoValidationError as e:
            return Response({'detail': e.message if hasattr(e, 'message') else str(e)},
                            status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.exception('Error saving tech eval doc for PL %s', pl_number)
            return Response({'detail': 'Upload failed. Check server logs.'},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        out = PLTechEvalDocumentSerializer(doc, context={'request': request})
        return Response(out.data, status=status.HTTP_201_CREATED)


class PLTechEvalDocDetailView(APIView):
    """
    DELETE /pl-master/{pl_number}/tech-eval-docs/{pk}/
    """
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request, pl_number, pk):
        doc = get_object_or_404(PLTechEvalDocument, pk=pk, pl_number=pl_number)
        file_name = doc.file_name
        try:
            doc.delete()   # also removes physical file from disk
        except Exception as e:
            logger.exception('Error deleting tech eval doc %s for PL %s', pk, pl_number)
            return Response({'detail': 'Delete failed.'},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        logger.info('Tech eval doc deleted: PL=%s file=%s by %s', pl_number, file_name, request.user)
        return Response(status=status.HTTP_204_NO_CONTENT)

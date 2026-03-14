# =============================================================================
# FILE: apps/pdf_tools/views.py
# SPRINT 6 — PDF Tools REST API
#
# POST /api/pdf/merge/      — queue merge job
# POST /api/pdf/split/      — queue split job
# POST /api/pdf/rotate/     — queue rotate job
# POST /api/pdf/extract/    — queue extract job
# GET  /api/pdf/jobs/       — list user's jobs
# GET  /api/pdf/jobs/{id}/  — job detail + output_files for download
# GET  /api/pdf/jobs/{id}/download/{idx}/ — stream output file
# =============================================================================
from django.http import FileResponse
from django.conf import settings
from pathlib     import Path
from django.utils import timezone
from django.shortcuts import get_object_or_404
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response   import Response

from apps.pdf_tools.models      import PdfJob
from apps.pdf_tools.serializers import (
    PdfJobSerializer,
    MergeRequestSerializer, SplitRequestSerializer,
    RotateRequestSerializer, ExtractRequestSerializer,
)
from apps.edms.models import FileAttachment
from apps.core.permissions import IsEngineerOrAbove


class PdfJobViewSet(viewsets.GenericViewSet,
                    viewsets.mixins.ListModelMixin,
                    viewsets.mixins.RetrieveModelMixin):
    serializer_class   = PdfJobSerializer
    permission_classes = [permissions.IsAuthenticated, IsEngineerOrAbove]

    def get_queryset(self):
        return PdfJob.objects.filter(created_by=self.request.user).select_related(
            'created_by', 'linked_revision'
        )

    # ---------------------------------------------------------------- MERGE
    @action(detail=False, methods=['post'], url_path='merge')
    def merge(self, request):
        ser = MergeRequestSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        d = ser.validated_data

        attachments = FileAttachment.objects.filter(pk__in=d['file_attachment_ids'])
        if attachments.count() != len(d['file_attachment_ids']):
            return Response({'error': 'One or more FileAttachment IDs not found.'},
                            status=status.HTTP_404_NOT_FOUND)

        # Preserve order from request
        id_order = {pk: i for i, pk in enumerate(d['file_attachment_ids'])}
        files    = sorted(attachments, key=lambda a: id_order[a.pk])
        paths    = [str(a.file_path) for a in files]

        job = PdfJob.objects.create(
            operation         = PdfJob.Operation.MERGE,
            input_files       = paths,
            params            = {'output_name': d['output_name']},
            created_by        = request.user,
            linked_revision_id = d.get('linked_revision_id'),
        )
        from apps.pdf_tools.tasks import run_pdf_job
        run_pdf_job.delay(job.pk)
        return Response(PdfJobSerializer(job).data, status=status.HTTP_202_ACCEPTED)

    # ---------------------------------------------------------------- SPLIT
    @action(detail=False, methods=['post'], url_path='split')
    def split(self, request):
        ser = SplitRequestSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        d   = ser.validated_data
        att = get_object_or_404(FileAttachment, pk=d['file_attachment_id'])

        job = PdfJob.objects.create(
            operation   = PdfJob.Operation.SPLIT,
            input_files = [str(att.file_path)],
            params      = {
                'page_ranges':      d.get('page_ranges'),
                'pages_per_chunk':  d.get('pages_per_chunk'),
            },
            created_by  = request.user,
        )
        from apps.pdf_tools.tasks import run_pdf_job
        run_pdf_job.delay(job.pk)
        return Response(PdfJobSerializer(job).data, status=status.HTTP_202_ACCEPTED)

    # ---------------------------------------------------------------- ROTATE
    @action(detail=False, methods=['post'], url_path='rotate')
    def rotate(self, request):
        ser = RotateRequestSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        d   = ser.validated_data
        att = get_object_or_404(FileAttachment, pk=d['file_attachment_id'])

        job = PdfJob.objects.create(
            operation   = PdfJob.Operation.ROTATE,
            input_files = [str(att.file_path)],
            params      = {
                'angle':        d['angle'],
                'page_numbers': d.get('page_numbers'),
                'output_name':  'rotated.pdf',
            },
            created_by  = request.user,
        )
        from apps.pdf_tools.tasks import run_pdf_job
        run_pdf_job.delay(job.pk)
        return Response(PdfJobSerializer(job).data, status=status.HTTP_202_ACCEPTED)

    # ---------------------------------------------------------------- EXTRACT
    @action(detail=False, methods=['post'], url_path='extract')
    def extract(self, request):
        ser = ExtractRequestSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        d   = ser.validated_data
        att = get_object_or_404(FileAttachment, pk=d['file_attachment_id'])

        job = PdfJob.objects.create(
            operation   = PdfJob.Operation.EXTRACT,
            input_files = [str(att.file_path)],
            params      = {
                'page_numbers': d['page_numbers'],
                'output_name':  d['output_name'],
            },
            created_by  = request.user,
        )
        from apps.pdf_tools.tasks import run_pdf_job
        run_pdf_job.delay(job.pk)
        return Response(PdfJobSerializer(job).data, status=status.HTTP_202_ACCEPTED)

    # ---------------------------------------------------------------- DOWNLOAD
    @action(detail=True, methods=['get'], url_path=r'download/(?P<file_idx>[0-9]+)')
    def download(self, request, pk=None, file_idx=None):
        job = self.get_object()
        if job.status != PdfJob.JobStatus.DONE:
            return Response({'error': 'Job not complete yet.'},
                            status=status.HTTP_400_BAD_REQUEST)
        idx = int(file_idx)
        if idx >= len(job.output_files):
            return Response({'error': 'File index out of range.'},
                            status=status.HTTP_404_NOT_FOUND)
        file_path = Path(settings.MEDIA_ROOT) / job.output_files[idx]
        if not file_path.exists():
            return Response({'error': 'Output file not found on disk.'},
                            status=status.HTTP_404_NOT_FOUND)
        return FileResponse(
            open(file_path, 'rb'),
            as_attachment=True,
            filename=file_path.name,
        )

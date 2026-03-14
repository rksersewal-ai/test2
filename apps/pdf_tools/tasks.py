# =============================================================================
# FILE: apps/pdf_tools/tasks.py
# SPRINT 6 — Celery tasks for async PDF operations
# =============================================================================
from celery import shared_task
import logging

log = logging.getLogger('pdf_tools')


@shared_task(name='pdf.run_job', bind=True, max_retries=1)
def run_pdf_job(self, job_id: int):
    """
    Execute a queued PdfJob.
    Updates status to RUNNING → DONE / FAILED.
    """
    from django.utils import timezone
    from apps.pdf_tools.models  import PdfJob
    from apps.pdf_tools.engine  import merge_pdfs, split_pdf, rotate_pdf, extract_pages

    try:
        job = PdfJob.objects.get(pk=job_id)
    except PdfJob.DoesNotExist:
        log.error(f'[PDF] PdfJob #{job_id} not found')
        return

    job.status = PdfJob.JobStatus.RUNNING
    job.save(update_fields=['status'])

    try:
        op     = job.operation
        inputs = job.input_files
        params = job.params

        if op == PdfJob.Operation.MERGE:
            output = merge_pdfs(inputs, output_name=params.get('output_name', 'merged.pdf'))
            job.output_files = [output]

        elif op == PdfJob.Operation.SPLIT:
            outputs = split_pdf(
                inputs[0],
                page_ranges     = params.get('page_ranges'),
                pages_per_chunk = params.get('pages_per_chunk'),
            )
            job.output_files = outputs

        elif op == PdfJob.Operation.ROTATE:
            output = rotate_pdf(
                inputs[0],
                angle        = params['angle'],
                page_numbers = params.get('page_numbers'),
                output_name  = params.get('output_name', 'rotated.pdf'),
            )
            job.output_files = [output]

        elif op == PdfJob.Operation.EXTRACT:
            output = extract_pages(
                inputs[0],
                page_numbers = params['page_numbers'],
                output_name  = params.get('output_name', 'extracted.pdf'),
            )
            job.output_files = [output]

        job.status       = PdfJob.JobStatus.DONE
        job.completed_at = timezone.now()
        job.save(update_fields=['status', 'output_files', 'completed_at'])
        log.info(f'[PDF] Job #{job_id} [{op}] DONE')

    except Exception as exc:
        job.status        = PdfJob.JobStatus.FAILED
        job.error_message = str(exc)
        job.completed_at  = timezone.now()
        job.save(update_fields=['status', 'error_message', 'completed_at'])
        log.error(f'[PDF] Job #{job_id} FAILED: {exc}')
        raise self.retry(exc=exc, countdown=10)

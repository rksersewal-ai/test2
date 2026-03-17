# =============================================================================
# FILE: apps/ocr/management/commands/recompute_missing_checksums.py
# FIX #4b: DB polling fallback for FileAttachment records whose
#   checksum_sha256 is blank because Celery/Redis was down at upload time.
#
# Usage (manual):
#   python manage.py recompute_missing_checksums
#   python manage.py recompute_missing_checksums --older-than 10  # minutes
#   python manage.py recompute_missing_checksums --dry-run
#
# Automated schedule:
#   Registered as a django-celery-beat PeriodicTask in apps/ocr/apps.py
#   via the ready() signal — runs every 15 minutes.
# =============================================================================
import hashlib
import logging
import os
from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = (
        'Recompute SHA-256 checksums for FileAttachment records where '
        'checksum_sha256 is blank (Celery was unavailable at upload time).'
    )

    def add_arguments(self, parser):
        parser.add_argument(
            '--older-than',
            type=int,
            default=5,
            metavar='MINUTES',
            help='Only process attachments uploaded more than N minutes ago '
                 '(default: 5). Avoids racing with an in-progress upload.',
        )
        parser.add_argument(
            '--batch-size',
            type=int,
            default=50,
            metavar='N',
            help='Maximum number of attachments to process per run (default: 50).',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            default=False,
            help='Print which attachments would be processed without writing to DB.',
        )

    def handle(self, *args, **options):
        from apps.edms.models import FileAttachment

        older_than  = options['older_than']
        batch_size  = options['batch_size']
        dry_run     = options['dry_run']
        cutoff_time = timezone.now() - timedelta(minutes=older_than)

        candidates = (
            FileAttachment.objects
            .filter(
                checksum_sha256='',
                uploaded_at__lt=cutoff_time,
            )
            .order_by('uploaded_at')
            [:batch_size]
        )

        total = candidates.count()
        if total == 0:
            self.stdout.write(self.style.SUCCESS('No missing checksums found.'))
            return

        self.stdout.write(
            f'Found {total} attachment(s) with missing checksum '
            f'(older than {older_than} min){" [DRY RUN]" if dry_run else ""}.'
        )

        updated = 0
        errors  = 0

        for attachment in candidates:
            try:
                physical_path = attachment.file_path.path
            except (ValueError, AttributeError):
                logger.warning(
                    'recompute_missing_checksums: invalid path for attachment %s, skipping.',
                    attachment.pk,
                )
                errors += 1
                continue

            if not os.path.exists(physical_path):
                logger.warning(
                    'recompute_missing_checksums: file missing on disk for attachment %s (%s), skipping.',
                    attachment.pk, attachment.file_name,
                )
                errors += 1
                continue

            sha256 = hashlib.sha256()
            try:
                with open(physical_path, 'rb') as f:
                    for chunk in iter(lambda: f.read(65536), b''):
                        sha256.update(chunk)
            except OSError as exc:
                logger.error(
                    'recompute_missing_checksums: OS error reading attachment %s: %s',
                    attachment.pk, exc,
                )
                errors += 1
                continue

            checksum = sha256.hexdigest()

            if dry_run:
                self.stdout.write(
                    f'  [DRY RUN] attachment {attachment.pk} ({attachment.file_name}) '
                    f'→ {checksum}'
                )
            else:
                FileAttachment.objects.filter(pk=attachment.pk).update(
                    checksum_sha256=checksum
                )
                logger.info(
                    'recompute_missing_checksums: computed checksum for attachment %s: %s',
                    attachment.pk, checksum,
                )
                updated += 1

        if not dry_run:
            self.stdout.write(
                self.style.SUCCESS(
                    f'Done. Updated: {updated}, Skipped/Errors: {errors}.'
                )
            )

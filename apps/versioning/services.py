# =============================================================================
# FILE: apps/versioning/services.py
# FR-006: Business logic for document versioning
# Handles create version, rollback, soft-delete recovery,
# version comparison, and next version number calculation.
# =============================================================================
import hashlib
import difflib
from datetime import timedelta
from django.utils import timezone
from django.db import transaction
from apps.edms.models import Document
from .models import DocumentVersion, VersionAnnotation, VersionDiff


class VersioningService:

    @staticmethod
    def _compute_sha256(file_obj) -> str:
        """Compute SHA-256 checksum of a file object."""
        hasher = hashlib.sha256()
        for chunk in file_obj.chunks():
            hasher.update(chunk)
        file_obj.seek(0)
        return hasher.hexdigest()

    @staticmethod
    def next_version_number(document: Document, major: bool = False) -> str:
        """Calculate next semantic version number (e.g., 1.0 → 1.1 or 2.0)."""
        latest = DocumentVersion.objects.filter(
            document=document
        ).exclude(status=DocumentVersion.VersionStatus.DELETED).order_by('-created_at').first()
        if not latest:
            return '1.0'
        try:
            major_n, minor_n = latest.version_number.split('.')
            major_n, minor_n = int(major_n), int(minor_n)
        except (ValueError, AttributeError):
            return '1.0'
        if major:
            return f'{major_n + 1}.0'
        return f'{major_n}.{minor_n + 1}'

    @staticmethod
    @transaction.atomic
    def create_version(document: Document, file_obj,
                       edit_summary: str = '', user=None,
                       major: bool = False) -> DocumentVersion:
        """Create a new version, archive previous current, compute checksum."""
        DocumentVersion.objects.filter(
            document=document, status=DocumentVersion.VersionStatus.CURRENT
        ).update(status=DocumentVersion.VersionStatus.PREVIOUS)

        version_number = VersioningService.next_version_number(document, major=major)
        checksum = VersioningService._compute_sha256(file_obj)

        version = DocumentVersion.objects.create(
            document=document,
            version_number=version_number,
            file_path=file_obj,
            file_size_bytes=file_obj.size,
            checksum_sha256=checksum,
            status=DocumentVersion.VersionStatus.CURRENT,
            edit_summary=edit_summary,
            is_major=major,
            created_by=user,
        )
        return version

    @staticmethod
    @transaction.atomic
    def rollback(document: Document, target_version_number: str,
                 user=None, reason: str = '') -> DocumentVersion:
        """Roll back document to a specific previous version."""
        target = DocumentVersion.objects.get(
            document=document, version_number=target_version_number
        )
        DocumentVersion.objects.filter(
            document=document, status=DocumentVersion.VersionStatus.CURRENT
        ).update(status=DocumentVersion.VersionStatus.PREVIOUS)

        rollback_number = VersioningService.next_version_number(document)
        rollback_version = DocumentVersion.objects.create(
            document=document,
            version_number=rollback_number,
            file_path=target.file_path,
            file_size_bytes=target.file_size_bytes,
            checksum_sha256=target.checksum_sha256,
            status=DocumentVersion.VersionStatus.CURRENT,
            edit_summary=f'Rollback to v{target_version_number}. Reason: {reason}',
            is_major=False,
            created_by=user,
        )
        if reason:
            VersionAnnotation.objects.create(
                version=rollback_version,
                text=f'Rolled back from v{target_version_number}: {reason}',
                created_by=user,
            )
        return rollback_version

    @staticmethod
    def soft_delete(version: DocumentVersion, user=None):
        """Soft-delete a version (recoverable for 30 days)."""
        version.status     = DocumentVersion.VersionStatus.DELETED
        version.deleted_at = timezone.now()
        version.save(update_fields=['status', 'deleted_at'])

    @staticmethod
    def recover(version: DocumentVersion):
        """Recover a soft-deleted version if within 30-day window."""
        if not version.deleted_at:
            raise ValueError('Version is not deleted.')
        if timezone.now() - version.deleted_at > timedelta(days=30):
            raise ValueError('Recovery window (30 days) has expired.')
        version.status     = DocumentVersion.VersionStatus.PREVIOUS
        version.deleted_at = None
        version.save(update_fields=['status', 'deleted_at'])

    @staticmethod
    def compare(version_a: DocumentVersion, version_b: DocumentVersion) -> str:
        """Generate unified diff between two versions' edit summaries as a lightweight comparison."""
        a_lines = (version_a.edit_summary or '').splitlines(keepends=True)
        b_lines = (version_b.edit_summary or '').splitlines(keepends=True)
        diff = list(difflib.unified_diff(
            a_lines, b_lines,
            fromfile=f'v{version_a.version_number}',
            tofile=f'v{version_b.version_number}',
        ))
        diff_text = ''.join(diff)
        VersionDiff.objects.update_or_create(
            from_version=version_a,
            to_version=version_b,
            defaults={'diff_content': diff_text, 'diff_size': len(diff_text)}
        )
        return diff_text

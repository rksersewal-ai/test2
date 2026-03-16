# =============================================================================
# FILE: tests/test_versioning.py
# FR-006: Unit tests for Document Versioning
# Covers: version numbering, create, archive previous, checksum,
#         rollback, annotation, soft-delete, 30-day recovery, compare,
#         and AlterationHistory entry creation (PRD Table 13.9).
# =============================================================================
import pytest
from io import BytesIO
from django.core.files.uploadedfile import InMemoryUploadedFile
from apps.versioning.models import DocumentVersion, AlterationHistory, VersionAnnotation
from apps.versioning.services import VersioningService
from tests.factories import UserFactory, DocumentFactory


def make_file(content: bytes = b'PDF content', name: str = 'test.pdf') -> InMemoryUploadedFile:
    buf = BytesIO(content)
    return InMemoryUploadedFile(buf, 'file', name, 'application/pdf', len(content), None)


@pytest.mark.django_db
class TestVersionNumbering:

    def test_first_version_is_1_0(self):
        doc = DocumentFactory()
        assert VersioningService.next_version_number(doc) == '1.0'

    def test_minor_bump(self):
        user = UserFactory()
        doc  = DocumentFactory()
        VersioningService.create_version(doc, make_file(b'v1'), 'Init', user)
        assert VersioningService.next_version_number(doc) == '1.1'

    def test_major_bump(self):
        user = UserFactory()
        doc  = DocumentFactory()
        VersioningService.create_version(doc, make_file(b'v1'), 'Init', user)
        assert VersioningService.next_version_number(doc, major=True) == '2.0'


@pytest.mark.django_db
class TestCreateVersion:

    def test_status_is_current(self):
        user = UserFactory()
        doc  = DocumentFactory()
        ver  = VersioningService.create_version(doc, make_file(b'v1'), 'First', user)
        assert ver.status == DocumentVersion.VersionStatus.CURRENT
        assert ver.version_number == '1.0'

    def test_previous_version_archived(self):
        user = UserFactory()
        doc  = DocumentFactory()
        v1 = VersioningService.create_version(doc, make_file(b'v1'), 'v1', user)
        VersioningService.create_version(doc, make_file(b'v2'), 'v2', user)
        v1.refresh_from_db()
        assert v1.status == DocumentVersion.VersionStatus.PREVIOUS

    def test_sha256_checksum(self):
        import hashlib
        user    = UserFactory()
        doc     = DocumentFactory()
        content = b'deterministic content'
        ver     = VersioningService.create_version(doc, make_file(content), 'chk', user)
        assert ver.checksum_sha256 == hashlib.sha256(content).hexdigest()

    def test_alteration_history_created(self):
        user = UserFactory()
        doc  = DocumentFactory()
        VersioningService.create_version(
            doc, make_file(b'v1'), 'Initial release',
            user=user, alteration_number='00',
            source_agency='CLW', change_reason='Initial issue'
        )
        assert AlterationHistory.objects.filter(
            document=doc, alteration_number='00'
        ).exists()


@pytest.mark.django_db
class TestRollback:

    def test_rollback_creates_new_version(self):
        user = UserFactory()
        doc  = DocumentFactory()
        VersioningService.create_version(doc, make_file(b'v1'), 'v1', user)
        VersioningService.create_version(doc, make_file(b'v2'), 'v2', user)
        rolled = VersioningService.rollback(doc, '1.0', user=user, reason='v1.1 had error')
        assert rolled.version_number == '1.2'
        assert rolled.status == DocumentVersion.VersionStatus.CURRENT

    def test_rollback_annotation(self):
        user = UserFactory()
        doc  = DocumentFactory()
        VersioningService.create_version(doc, make_file(b'v1'), 'v1', user)
        VersioningService.create_version(doc, make_file(b'v2'), 'v2', user)
        VersioningService.rollback(doc, '1.0', user=user, reason='Correction needed')
        assert VersionAnnotation.objects.filter(
            version__document=doc, text__icontains='Rollback'
        ).exists()


@pytest.mark.django_db
class TestSoftDeleteRecovery:

    def test_soft_delete_sets_status(self):
        user = UserFactory()
        doc  = DocumentFactory()
        ver  = VersioningService.create_version(doc, make_file(b'v1'), 'v1', user)
        VersioningService.soft_delete(ver)
        ver.refresh_from_db()
        assert ver.status == DocumentVersion.VersionStatus.DELETED
        assert ver.deleted_at is not None

    def test_recover_within_30_days(self):
        user = UserFactory()
        doc  = DocumentFactory()
        ver  = VersioningService.create_version(doc, make_file(b'v1'), 'v1', user)
        VersioningService.soft_delete(ver)
        VersioningService.recover(ver)
        ver.refresh_from_db()
        assert ver.status == DocumentVersion.VersionStatus.PREVIOUS
        assert ver.deleted_at is None

    def test_recover_after_30_days_raises(self):
        from datetime import timedelta
        from django.utils import timezone
        user = UserFactory()
        doc  = DocumentFactory()
        ver  = VersioningService.create_version(doc, make_file(b'v1'), 'v1', user)
        VersioningService.soft_delete(ver)
        ver.deleted_at = timezone.now() - timedelta(days=31)
        ver.save()
        with pytest.raises(ValueError, match='Recovery window'):
            VersioningService.recover(ver)


@pytest.mark.django_db
class TestCompare:

    def test_compare_returns_diff_string(self):
        user = UserFactory()
        doc  = DocumentFactory()
        v1   = VersioningService.create_version(doc, make_file(b'v1'), 'Initial draft', user)
        v2   = VersioningService.create_version(doc, make_file(b'v2'), 'Corrected layout', user)
        diff = VersioningService.compare(v1, v2)
        assert isinstance(diff, str)

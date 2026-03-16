# =============================================================================
# FILE: tests/test_versioning.py
# FR-006: Tests for Document Versioning module
# Covers version creation, next version numbering, rollback,
# soft-delete, recovery, compare/diff, and annotations.
# =============================================================================
import pytest
from io import BytesIO
from django.core.files.uploadedfile import InMemoryUploadedFile
from apps.versioning.models import DocumentVersion, VersionAnnotation
from apps.versioning.services import VersioningService
from tests.factories import UserFactory, DocumentFactory


def make_file(content: bytes = b'PDF content v1', name: str = 'test.pdf') -> InMemoryUploadedFile:
    buf = BytesIO(content)
    return InMemoryUploadedFile(
        buf, 'file', name, 'application/pdf', len(content), None
    )


@pytest.mark.django_db
class TestVersionNumbering:

    def test_first_version_is_1_0(self):
        document = DocumentFactory()
        assert VersioningService.next_version_number(document) == '1.0'

    def test_minor_bump(self):
        user     = UserFactory()
        document = DocumentFactory()
        VersioningService.create_version(document, make_file(b'v1'), 'Initial', user)
        assert VersioningService.next_version_number(document) == '1.1'

    def test_major_bump(self):
        user     = UserFactory()
        document = DocumentFactory()
        VersioningService.create_version(document, make_file(b'v1'), 'Initial', user)
        assert VersioningService.next_version_number(document, major=True) == '2.0'


@pytest.mark.django_db
class TestCreateVersion:

    def test_create_sets_current_status(self):
        user     = UserFactory()
        document = DocumentFactory()
        ver = VersioningService.create_version(
            document, make_file(b'content'), 'First upload', user
        )
        assert ver.status == DocumentVersion.VersionStatus.CURRENT
        assert ver.version_number == '1.0'

    def test_previous_version_archived(self):
        user     = UserFactory()
        document = DocumentFactory()
        v1 = VersioningService.create_version(document, make_file(b'v1'), 'v1', user)
        VersioningService.create_version(document, make_file(b'v2'), 'v2', user)
        v1.refresh_from_db()
        assert v1.status == DocumentVersion.VersionStatus.PREVIOUS

    def test_checksum_computed(self):
        user     = UserFactory()
        document = DocumentFactory()
        ver = VersioningService.create_version(
            document, make_file(b'hello world'), 'checksum test', user
        )
        assert len(ver.checksum_sha256) == 64


@pytest.mark.django_db
class TestRollback:

    def test_rollback_creates_new_version(self):
        user     = UserFactory()
        document = DocumentFactory()
        VersioningService.create_version(document, make_file(b'v1'), 'v1', user)
        VersioningService.create_version(document, make_file(b'v2'), 'v2', user)
        rolled = VersioningService.rollback(document, '1.0', user=user, reason='Testing rollback')
        assert rolled.version_number == '1.2'
        assert rolled.status == DocumentVersion.VersionStatus.CURRENT

    def test_rollback_creates_annotation(self):
        user     = UserFactory()
        document = DocumentFactory()
        VersioningService.create_version(document, make_file(b'v1'), 'v1', user)
        VersioningService.create_version(document, make_file(b'v2'), 'v2', user)
        VersioningService.rollback(document, '1.0', user=user, reason='Mistake in v1.1')
        assert VersionAnnotation.objects.filter(
            version__document=document,
            text__icontains='Rollback'
        ).exists()


@pytest.mark.django_db
class TestSoftDeleteAndRecovery:

    def test_soft_delete(self):
        user     = UserFactory()
        document = DocumentFactory()
        ver = VersioningService.create_version(document, make_file(b'v1'), 'v1', user)
        VersioningService.soft_delete(ver)
        ver.refresh_from_db()
        assert ver.status == DocumentVersion.VersionStatus.DELETED
        assert ver.deleted_at is not None

    def test_recover_within_window(self):
        user     = UserFactory()
        document = DocumentFactory()
        ver = VersioningService.create_version(document, make_file(b'v1'), 'v1', user)
        VersioningService.soft_delete(ver)
        VersioningService.recover(ver)
        ver.refresh_from_db()
        assert ver.status == DocumentVersion.VersionStatus.PREVIOUS
        assert ver.deleted_at is None

    def test_recover_after_30_days_raises(self):
        from datetime import timedelta
        from django.utils import timezone
        user     = UserFactory()
        document = DocumentFactory()
        ver = VersioningService.create_version(document, make_file(b'v1'), 'v1', user)
        VersioningService.soft_delete(ver)
        ver.deleted_at = timezone.now() - timedelta(days=31)
        ver.save()
        with pytest.raises(ValueError, match='Recovery window'):
            VersioningService.recover(ver)


@pytest.mark.django_db
class TestVersionCompare:

    def test_compare_produces_diff(self):
        user     = UserFactory()
        document = DocumentFactory()
        v1 = VersioningService.create_version(
            document, make_file(b'v1'), 'Initial draft uploaded', user
        )
        v2 = VersioningService.create_version(
            document, make_file(b'v2'), 'Updated with corrections', user
        )
        diff = VersioningService.compare(v1, v2)
        assert isinstance(diff, str)

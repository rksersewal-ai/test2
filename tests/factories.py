"""
Factory-boy factories for all core models.

Usage:
    from tests.factories import DocumentFactory, UserFactory, DocumentTypeFactory
    doc = DocumentFactory()                                  # saved to DB
    doc = DocumentFactory(document_type=DocumentTypeFactory())
"""
import factory
from factory.django import DjangoModelFactory
from django.utils import timezone
from apps.core.models import User, Section
from apps.edms.models import Document, DocumentType, Revision, FileAttachment
from apps.workflow.models import WorkType, WorkLedgerEntry
from apps.ocr.models import OCRQueue, OCRResult
from apps.audit.models import AuditLog


class SectionFactory(DjangoModelFactory):
    class Meta:
        model = Section
        django_get_or_create = ('code',)

    code = factory.Sequence(lambda n: f'SEC{n:03d}')
    name = factory.LazyAttribute(lambda o: f'Section {o.code}')


class UserFactory(DjangoModelFactory):
    class Meta:
        model = User

    username   = factory.Sequence(lambda n: f'user{n}')
    full_name  = factory.LazyAttribute(lambda o: f'User {o.username.title()}')
    email      = factory.LazyAttribute(lambda o: f'{o.username}@plw.railnet')
    role       = User.Role.ENGINEER
    section    = factory.SubFactory(SectionFactory)
    is_active  = True
    password   = factory.PostGenerationMethodCall('set_password', 'Test@12345')


class AdminUserFactory(UserFactory):
    role = User.Role.ADMIN
    is_staff = True
    is_superuser = True


class DocumentTypeFactory(DjangoModelFactory):
    """Factory for apps.edms.models.DocumentType.
    Used by MetadataField and Phase 1 tests.
    """
    class Meta:
        model = DocumentType
        django_get_or_create = ('code',)

    code      = factory.Sequence(lambda n: f'DT{n:03d}')
    name      = factory.LazyAttribute(lambda o: f'Document Type {o.code}')
    is_active = True


class DocumentFactory(DjangoModelFactory):
    """Factory for apps.edms.models.Document.
    Uses the correct field names from the amended PRD schema:
      - document_number  (not doc_number)
      - document_type FK (not doc_type CharField)
    """
    class Meta:
        model = Document

    document_number = factory.Sequence(lambda n: f'PLW/TEST/2024/{n:04d}')
    title           = factory.LazyAttribute(lambda o: f'Test Document {o.document_number}')
    document_type   = factory.SubFactory(DocumentTypeFactory)
    status          = Document.Status.ACTIVE
    section         = factory.SubFactory(SectionFactory)
    created_by      = factory.SubFactory(UserFactory)


class RevisionFactory(DjangoModelFactory):
    class Meta:
        model = Revision

    document        = factory.SubFactory(DocumentFactory)
    revision_number = factory.Sequence(lambda n: f'R{n:02d}')
    status          = Revision.Status.CURRENT
    created_by      = factory.SubFactory(UserFactory)
    revision_date   = factory.LazyFunction(lambda: timezone.now().date())


class FileAttachmentFactory(DjangoModelFactory):
    class Meta:
        model = FileAttachment

    revision        = factory.SubFactory(RevisionFactory)
    file_name       = factory.Sequence(lambda n: f'test_file_{n}.pdf')
    file_size_bytes = 102400
    file_type       = FileAttachment.FileType.PDF
    uploaded_by     = factory.SubFactory(UserFactory)


class WorkTypeFactory(DjangoModelFactory):
    class Meta:
        model = WorkType
        django_get_or_create = ('code',)

    name      = factory.Sequence(lambda n: f'Work Type {n}')
    code      = factory.Sequence(lambda n: f'WK{n:03d}')
    is_active = True


class WorkLedgerEntryFactory(DjangoModelFactory):
    class Meta:
        model = WorkLedgerEntry

    subject       = factory.Sequence(lambda n: f'Work Entry {n}')
    status        = 'OPEN'
    work_type     = factory.SubFactory(WorkTypeFactory)
    section       = factory.SubFactory(SectionFactory)
    created_by    = factory.SubFactory(UserFactory)
    received_date = factory.LazyFunction(timezone.now)


class OCRQueueFactory(DjangoModelFactory):
    class Meta:
        model = OCRQueue

    status   = 'PENDING'
    priority = 5


class OCRResultFactory(DjangoModelFactory):
    class Meta:
        model = OCRResult

    queue_item  = factory.SubFactory(OCRQueueFactory)
    full_text   = 'PLW/SPEC/2024/0001 RDSO/PE/SPEC/TL/0013 IS:3043-2019'
    confidence  = 92.5
    page_count  = 3


class AuditLogFactory(DjangoModelFactory):
    class Meta:
        model = AuditLog

    user        = factory.SubFactory(UserFactory)
    username    = factory.LazyAttribute(lambda o: o.user.username)
    module      = AuditLog.Module.EDMS
    action      = 'DOCUMENT_CREATE'
    entity_type = 'Document'
    entity_id   = factory.Sequence(lambda n: n)
    success     = True

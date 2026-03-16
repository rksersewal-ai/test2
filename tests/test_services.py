import pytest
from apps.edms.services import DocumentService
from tests.factories import DocumentFactory, RevisionFactory

@pytest.mark.django_db
class TestDocumentService:
    def test_next_revision_number(self):
        # Create a document
        doc = DocumentFactory.create()

        # Test with no revisions
        assert DocumentService.next_revision_number(doc) == "00"

        # Add 1 revision
        RevisionFactory.create(document=doc)
        assert DocumentService.next_revision_number(doc) == "01"

        # Add a bunch of revisions to test zfill
        for _ in range(8):
            RevisionFactory.create(document=doc)
        assert DocumentService.next_revision_number(doc) == "09"

        # One more makes 10
        RevisionFactory.create(document=doc)
        assert DocumentService.next_revision_number(doc) == "10"

        # And over 10 doesn't get messed up
        for _ in range(90):
            RevisionFactory.create(document=doc)
        assert DocumentService.next_revision_number(doc) == "100"

import pytest
from unittest.mock import patch, MagicMock
from apps.edms.services import DocumentService

class TestDocumentService:
    @patch('apps.edms.services.AuditService')
    def test_update_status(self, mock_audit_service):
        # Create user and document mock
        doc_mock = MagicMock()
        doc_mock.status = 'ACTIVE'
        doc_mock.document_number = 'DOC-123'
        doc_mock.pk = 1

        user_mock = MagicMock()
        user_mock.username = 'testuser'

        # We mock get_connection to bypass the autocommit check within transaction.atomic
        with patch('django.db.transaction.get_connection') as mock_conn:
            mock_conn.return_value.get_autocommit.return_value = True

            # Call update_status normally
            result = DocumentService.update_status(doc_mock, 'OBSOLETE', user_mock)

            # Verify document updates
            assert result == doc_mock
            assert doc_mock.status == 'OBSOLETE'
            doc_mock.save.assert_called_once_with(update_fields=['status', 'updated_at'])

            # Verify AuditLog call
            mock_audit_service.log.assert_called_once_with(
                user=user_mock,
                module='EDMS',
                action='UPDATE_STATUS',
                entity_type='Document',
                entity_id=1,
                entity_identifier='DOC-123',
                description='Status changed ACTIVE → OBSOLETE.'
            )

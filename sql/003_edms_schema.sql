-- Migration 003: EDMS schema - Document, Revision, FileAttachment indexes

CREATE INDEX IF NOT EXISTS idx_edms_document_number ON edms_document(document_number);
CREATE INDEX IF NOT EXISTS idx_edms_document_status ON edms_document(status);
CREATE INDEX IF NOT EXISTS idx_edms_document_eoffice ON edms_document(eoffice_file_number) WHERE eoffice_file_number != '';
CREATE INDEX IF NOT EXISTS idx_edms_document_section ON edms_document(section_id);

-- Trigram index for full-text title/keyword search
CREATE INDEX IF NOT EXISTS idx_edms_document_title_trgm ON edms_document USING gin(title gin_trgm_ops);
CREATE INDEX IF NOT EXISTS idx_edms_document_keywords_trgm ON edms_document USING gin(keywords gin_trgm_ops);

CREATE INDEX IF NOT EXISTS idx_edms_revision_document ON edms_revision(document_id);
CREATE INDEX IF NOT EXISTS idx_edms_revision_status ON edms_revision(status);

CREATE INDEX IF NOT EXISTS idx_edms_file_revision ON edms_file_attachment(revision_id);
CREATE INDEX IF NOT EXISTS idx_edms_file_checksum ON edms_file_attachment(checksum_sha256) WHERE checksum_sha256 != '';

COMMENT ON TABLE edms_document IS 'Master document registry - PLW EDMS';
COMMENT ON TABLE edms_revision IS 'Document revision history';
COMMENT ON TABLE edms_file_attachment IS 'Physical file storage references';

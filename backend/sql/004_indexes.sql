-- ============================================================
-- PLW EDMS — PERFORMANCE INDEXES
-- File: 004_indexes.sql
-- Run order: 4th (after 001)
-- ============================================================

-- Users
CREATE INDEX idx_users_username ON public.users(username);
CREATE INDEX idx_users_email    ON public.users(email);
CREATE INDEX idx_users_section  ON public.users(section_id);
CREATE INDEX idx_users_active   ON public.users(is_active);

-- Sections
CREATE INDEX idx_sections_code   ON public.sections(code);
CREATE INDEX idx_sections_parent ON public.sections(parent_id);

-- Documents
CREATE INDEX idx_documents_number   ON edms.documents(document_number);
CREATE INDEX idx_documents_status   ON edms.documents(status);
CREATE INDEX idx_documents_type     ON edms.documents(document_type_id);
CREATE INDEX idx_documents_category ON edms.documents(category_id);
CREATE INDEX idx_documents_section  ON edms.documents(section_id);
CREATE INDEX idx_documents_created  ON edms.documents(created_at DESC);
CREATE INDEX idx_documents_archived ON edms.documents(is_archived);
CREATE INDEX idx_documents_keywords ON edms.documents USING gin(keywords);

-- Trigram indexes for full-text search
CREATE INDEX idx_documents_title_trgm ON edms.documents USING gin(title gin_trgm_ops);

-- Revisions
CREATE INDEX idx_revisions_document ON edms.revisions(document_id);
CREATE INDEX idx_revisions_number   ON edms.revisions(revision_number);
CREATE INDEX idx_revisions_status   ON edms.revisions(status);
CREATE INDEX idx_revisions_current  ON edms.revisions(is_current);

-- Files
CREATE INDEX idx_files_revision     ON edms.files(revision_id);
CREATE INDEX idx_files_type         ON edms.files(file_type);
CREATE INDEX idx_files_ocr          ON edms.files(is_ocr_processed);
CREATE INDEX idx_files_primary      ON edms.files(is_primary);
CREATE INDEX idx_files_ocr_trgm     ON edms.files USING gin(ocr_text gin_trgm_ops) WHERE ocr_text IS NOT NULL;

-- Work Ledger
CREATE INDEX idx_work_number    ON workflow.work_ledger(ledger_number);
CREATE INDEX idx_work_type      ON workflow.work_ledger(work_type_id);
CREATE INDEX idx_work_status    ON workflow.work_ledger(status);
CREATE INDEX idx_work_performer ON workflow.work_ledger(performed_by);
CREATE INDEX idx_work_section   ON workflow.work_ledger(section_id);
CREATE INDEX idx_work_document  ON workflow.work_ledger(document_id);
CREATE INDEX idx_work_dates     ON workflow.work_ledger(received_date, closed_date);
CREATE INDEX idx_work_eoffice   ON workflow.work_ledger(eoffice_file_number)
    WHERE eoffice_file_number IS NOT NULL;

-- Tenders
CREATE INDEX idx_tenders_number ON workflow.tenders(tender_number);
CREATE INDEX idx_tenders_status ON workflow.tenders(status);

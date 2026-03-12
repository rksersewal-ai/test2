-- Migration 006: Audit log schema - immutable, append-only enforcement

CREATE INDEX IF NOT EXISTS idx_audit_log_timestamp ON audit_log(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_audit_log_module_action ON audit_log(module, action);
CREATE INDEX IF NOT EXISTS idx_audit_log_username ON audit_log(username);
CREATE INDEX IF NOT EXISTS idx_audit_log_entity ON audit_log(entity_type, entity_id);

-- Prevent DELETE and UPDATE at DB level (belt-and-suspenders with model-level protection)
CREATE OR REPLACE RULE audit_log_no_update AS ON UPDATE TO audit_log DO INSTEAD NOTHING;
CREATE OR REPLACE RULE audit_log_no_delete AS ON DELETE TO audit_log DO INSTEAD NOTHING;

CREATE INDEX IF NOT EXISTS idx_doc_access_log_timestamp ON audit_document_access_log(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_doc_access_log_document ON audit_document_access_log(document_id);

CREATE OR REPLACE RULE doc_access_log_no_update AS ON UPDATE TO audit_document_access_log DO INSTEAD NOTHING;
CREATE OR REPLACE RULE doc_access_log_no_delete AS ON DELETE TO audit_document_access_log DO INSTEAD NOTHING;

COMMENT ON TABLE audit_log IS 'Immutable system audit trail - insert-only';
COMMENT ON TABLE audit_document_access_log IS 'Document access events - insert-only';

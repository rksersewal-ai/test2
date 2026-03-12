-- Migration 004: Workflow / LDO Work Ledger schema indexes

CREATE INDEX IF NOT EXISTS idx_workflow_ledger_status ON workflow_work_ledger(status);
CREATE INDEX IF NOT EXISTS idx_workflow_ledger_section ON workflow_work_ledger(section_id);
CREATE INDEX IF NOT EXISTS idx_workflow_ledger_eoffice ON workflow_work_ledger(eoffice_file_number) WHERE eoffice_file_number != '';
CREATE INDEX IF NOT EXISTS idx_workflow_ledger_received ON workflow_work_ledger(received_date);
CREATE INDEX IF NOT EXISTS idx_workflow_ledger_closed ON workflow_work_ledger(closed_date) WHERE closed_date IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_workflow_ledger_document ON workflow_work_ledger(document_id) WHERE document_id IS NOT NULL;

CREATE INDEX IF NOT EXISTS idx_workflow_tender_status ON workflow_tender(status);
CREATE INDEX IF NOT EXISTS idx_workflow_tender_eoffice ON workflow_tender(eoffice_file_number) WHERE eoffice_file_number != '';

COMMENT ON TABLE workflow_work_ledger IS 'LDO factual work record - neutral record-keeping, no approval engine';
COMMENT ON TABLE workflow_work_type IS 'Master work types for LDO operations';

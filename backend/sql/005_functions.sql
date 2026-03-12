-- ============================================================
-- PLW EDMS — DATABASE FUNCTIONS AND TRIGGERS
-- File: 005_functions.sql
-- Run order: 5th (after all others)
-- ============================================================

-- Auto-update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_sections_ts   BEFORE UPDATE ON public.sections    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_users_ts      BEFORE UPDATE ON public.users       FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_documents_ts  BEFORE UPDATE ON edms.documents     FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_revisions_ts  BEFORE UPDATE ON edms.revisions     FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_work_ts       BEFORE UPDATE ON workflow.work_ledger FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_vendors_ts    BEFORE UPDATE ON workflow.vendors    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_tenders_ts    BEFORE UPDATE ON workflow.tenders    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Auto-generate ledger number: LDO-YYYY-NNNNN
CREATE SEQUENCE IF NOT EXISTS workflow.ledger_number_seq START 1;

CREATE OR REPLACE FUNCTION workflow.generate_ledger_number()
RETURNS TRIGGER AS $$
DECLARE
    seq_val BIGINT;
    year_str TEXT;
BEGIN
    IF NEW.ledger_number IS NULL OR NEW.ledger_number = '' THEN
        seq_val  := nextval('workflow.ledger_number_seq');
        year_str := TO_CHAR(CURRENT_DATE, 'YYYY');
        NEW.ledger_number := 'LDO-' || year_str || '-' || LPAD(seq_val::TEXT, 5, '0');
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_generate_ledger_number
    BEFORE INSERT ON workflow.work_ledger
    FOR EACH ROW EXECUTE FUNCTION workflow.generate_ledger_number();

-- Enforce single current revision per document
CREATE OR REPLACE FUNCTION edms.enforce_single_current_revision()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.is_current = TRUE THEN
        UPDATE edms.revisions
        SET is_current = FALSE
        WHERE document_id = NEW.document_id
          AND id != NEW.id
          AND is_current = TRUE;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_enforce_single_current
    BEFORE INSERT OR UPDATE ON edms.revisions
    FOR EACH ROW EXECUTE FUNCTION edms.enforce_single_current_revision();

-- Seed LDO work types
INSERT INTO workflow.work_types (code, name, category, requires_document) VALUES
    ('DRW_REV',     'Implementation of Latest Drawing/Specification/Modification',         'drawing_revision',    TRUE),
    ('STR_DEV',     'STR Development for NVD Items',                                       'str_development',     TRUE),
    ('TENDER_EVAL', 'Technical Evaluation of Tenders',                                     'tender_support',      FALSE),
    ('ELIG_CRIT',   'Preparation of Eligibility Criteria',                                 'tender_support',      FALSE),
    ('CTRL_COPY',   'Issue of Controlled Copies of Drawings/Documents',                    'document_control',    TRUE),
    ('PROTO_REF',   'Prototype / CCA Record Reference',                                    'prototype',           FALSE),
    ('RDSO_MOD',    'Implementation of RDSO Modification Sheet',                           'rdso_modification',   TRUE),
    ('EXT_CORR',    'External Correspondence Reference',                                   'correspondence',      FALSE),
    ('BOM_UPDATE',  'BOM Update / Configuration Change',                                   'bom_management',      TRUE),
    ('INSP_REF',    'Inspection Reference / Test Report Linking',                          'inspection',          FALSE),
    ('SPEC_DEV',    'Specification Development',                                            'specification',       TRUE),
    ('VENDOR_REG',  'Vendor Registration / Approval Reference',                            'vendor_management',   FALSE);

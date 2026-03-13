-- =============================================================================
-- FILE: sql/004_work_ledger_core.sql
-- PURPOSE: Work Ledger core tables, indexes, constraint, views, and seed data
-- MODULE: LDO Work Ledger
-- PRIORITY: P0
-- DEPENDS ON: users table, documents table (if linking attachments to EDMS docs)
-- BACKWARD COMPATIBLE: Yes (new tables only)
-- DATA MIGRATION REQUIRED: No
-- =============================================================================

-- -----------------------------------------------------------------------
-- 1. WORK CATEGORY MASTER
-- -----------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS work_category_master (
    code        VARCHAR(60)  PRIMARY KEY,
    label       VARCHAR(150) NOT NULL,
    is_active   BOOLEAN      NOT NULL DEFAULT TRUE,
    sort_order  INTEGER      NOT NULL DEFAULT 0
);

-- Seed: All 18 official LDO work categories
INSERT INTO work_category_master (code, label, sort_order) VALUES
    ('TENDER_CASE_FILING',           'Tender Case Filing of Documents',          1),
    ('TECHNICAL_EVALUATION',         'Technical Evaluation',                     2),
    ('TECHNICAL_CLARIFICATION',      'Technical Clarification',                  3),
    ('ELIGIBILITY_CRITERIA_REVISION','Eligibility Criteria Revision',            4),
    ('DRAWING_MODIFICATION_OR_NEW',  'Modification in Drawing / New Drawing',    5),
    ('SPECIFICATION_MODIFICATION',   'Modification in Specification',            6),
    ('COMPLAINT_LETTER_TO_FIRM',     'Complaint Letter to Firm',                 7),
    ('LETTER_TO_RDSO_CLW_BLW_ICF',   'Letter to RDSO / CLW / BLW / ICF',        8),
    ('DEVELOPMENT_PO',               'Development PO',                           9),
    ('PROTOTYPE_INSPECTION',         'Prototype Inspection',                    10),
    ('DISPATCH_CLEARANCE_PROTOTYPE', 'Dispatch Clearance for Prototype',        11),
    ('SOURCE_DEVELOPMENT',           'Source Development',                      12),
    ('SHOP_VISIT',                   'Shop Visit',                              13),
    ('SPECIFICATION_STUDIED',        'Specification Studied',                   14),
    ('NEW_INNOVATION',               'New Innovation',                          15),
    ('ACHIEVEMENT',                  'Achievement',                             16),
    ('VISIT_TO_FIRM_PU_ZR',          'Visit to Firm / PU / ZR',                17),
    ('MISC',                         'Miscellaneous',                           18)
ON CONFLICT (code) DO NOTHING;

-- -----------------------------------------------------------------------
-- 2. WORK LEDGER (core record table)
-- -----------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS work_ledger (
    work_id                BIGSERIAL    PRIMARY KEY,
    work_code              VARCHAR(30)  NOT NULL UNIQUE,   -- e.g. WL-2026-000044
    received_date          DATE         NOT NULL,
    closed_date            DATE         NULL,
    section                VARCHAR(30)  NOT NULL,          -- Mechanical / Electrical
    engineer_id            BIGINT       NOT NULL,
    officer_id             BIGINT       NULL,
    status                 VARCHAR(20)  NOT NULL DEFAULT 'Open',
    pl_number              VARCHAR(60)  NULL,
    drawing_number         VARCHAR(120) NULL,
    drawing_revision       VARCHAR(20)  NULL,
    specification_number   VARCHAR(120) NULL,
    specification_revision VARCHAR(20)  NULL,
    tender_number          VARCHAR(120) NULL,
    case_number            VARCHAR(120) NULL,
    eoffice_file_no        VARCHAR(120) NULL,
    work_category_code     VARCHAR(60)  NOT NULL REFERENCES work_category_master(code),
    description            TEXT         NOT NULL,
    remarks                TEXT         NULL,
    created_by             BIGINT       NOT NULL,
    created_at             TIMESTAMP    NOT NULL DEFAULT NOW(),
    updated_at             TIMESTAMP    NOT NULL DEFAULT NOW(),
    CONSTRAINT chk_closed_date CHECK (
        closed_date IS NULL OR closed_date >= received_date
    ),
    CONSTRAINT chk_status CHECK (
        status IN ('Open', 'Closed', 'Pending')
    ),
    CONSTRAINT chk_section CHECK (
        section IN ('Mechanical', 'Electrical', 'General')
    )
);

-- -----------------------------------------------------------------------
-- 3. WORK LEDGER DETAIL (category-specific dynamic fields)
-- -----------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS work_ledger_detail (
    detail_id   BIGSERIAL   PRIMARY KEY,
    work_id     BIGINT      NOT NULL REFERENCES work_ledger(work_id) ON DELETE CASCADE,
    field_name  VARCHAR(100) NOT NULL,
    field_value TEXT         NULL,
    UNIQUE (work_id, field_name)
);

-- -----------------------------------------------------------------------
-- 4. WORK LEDGER ATTACHMENT
-- -----------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS work_ledger_attachment (
    attachment_id  BIGSERIAL    PRIMARY KEY,
    work_id        BIGINT       NOT NULL REFERENCES work_ledger(work_id) ON DELETE CASCADE,
    document_id    BIGINT       NULL,    -- optional link to EDMS document
    file_name      VARCHAR(255) NOT NULL,
    file_path      VARCHAR(600) NOT NULL,
    mime_type      VARCHAR(100) NULL,
    file_size_kb   INTEGER      NULL,
    uploaded_by    BIGINT       NOT NULL,
    uploaded_at    TIMESTAMP    NOT NULL DEFAULT NOW()
);

-- -----------------------------------------------------------------------
-- 5. INDEXES
-- -----------------------------------------------------------------------
CREATE INDEX IF NOT EXISTS idx_wl_received_date       ON work_ledger(received_date);
CREATE INDEX IF NOT EXISTS idx_wl_closed_date         ON work_ledger(closed_date);
CREATE INDEX IF NOT EXISTS idx_wl_section             ON work_ledger(section);
CREATE INDEX IF NOT EXISTS idx_wl_engineer_id         ON work_ledger(engineer_id);
CREATE INDEX IF NOT EXISTS idx_wl_officer_id          ON work_ledger(officer_id);
CREATE INDEX IF NOT EXISTS idx_wl_status              ON work_ledger(status);
CREATE INDEX IF NOT EXISTS idx_wl_category_code       ON work_ledger(work_category_code);
CREATE INDEX IF NOT EXISTS idx_wl_pl_number           ON work_ledger(pl_number);
CREATE INDEX IF NOT EXISTS idx_wl_tender_number       ON work_ledger(tender_number);
CREATE INDEX IF NOT EXISTS idx_wl_eoffice_file_no     ON work_ledger(eoffice_file_no);
CREATE INDEX IF NOT EXISTS idx_wld_work_id            ON work_ledger_detail(work_id);
CREATE INDEX IF NOT EXISTS idx_wla_work_id            ON work_ledger_attachment(work_id);

-- -----------------------------------------------------------------------
-- 6. AUTO-UPDATE updated_at TRIGGER
-- -----------------------------------------------------------------------
CREATE OR REPLACE FUNCTION fn_set_updated_at()
RETURNS TRIGGER LANGUAGE plpgsql AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$;

DROP TRIGGER IF EXISTS trg_work_ledger_updated_at ON work_ledger;
CREATE TRIGGER trg_work_ledger_updated_at
    BEFORE UPDATE ON work_ledger
    FOR EACH ROW EXECUTE FUNCTION fn_set_updated_at();

-- -----------------------------------------------------------------------
-- 7. REPORTING VIEWS
-- -----------------------------------------------------------------------

-- Activity report view (flat, for filtered tabular reporting)
CREATE OR REPLACE VIEW vw_work_ledger_activity AS
SELECT
    wl.work_id,
    wl.work_code,
    wl.received_date,
    wl.closed_date,
    wl.section,
    wl.status,
    wl.pl_number,
    wl.drawing_number,
    wl.tender_number,
    wl.eoffice_file_no,
    wl.work_category_code,
    wcm.label            AS work_category_label,
    wl.description,
    wl.remarks,
    wl.created_at
FROM work_ledger wl
JOIN work_category_master wcm ON wcm.code = wl.work_category_code;

-- Monthly KPI summary view
CREATE OR REPLACE VIEW vw_work_ledger_monthly_kpi AS
SELECT
    DATE_TRUNC('month', wl.received_date)::DATE  AS month_start,
    wl.work_category_code,
    wcm.label                                     AS work_category_label,
    wl.section,
    COUNT(*)                                      AS work_count
FROM work_ledger wl
JOIN work_category_master wcm ON wcm.code = wl.work_category_code
GROUP BY 1, 2, 3, 4;

-- =============================================================================
-- END: sql/004_work_ledger_core.sql
-- =============================================================================

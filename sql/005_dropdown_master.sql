-- =============================================================================
-- FILE: sql/005_dropdown_master.sql
-- PURPOSE: Universal admin-managed dropdown master table for all form dropdowns
-- MODULE: LDO Work Ledger - Dropdown Management
-- PRIORITY: P0
-- DESIGN: Single table with (group_key, code, label) pattern.
--         Admin can add/edit/soft-delete any item from any dropdown.
--         All dropdowns sorted alphabetically by label (default).
--         sort_override allows manual order override when alphabetical is not ideal.
-- =============================================================================

-- -----------------------------------------------------------------------
-- 1. MAIN TABLE
-- -----------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS dropdown_master (
    id              BIGSERIAL    PRIMARY KEY,
    group_key       VARCHAR(80)  NOT NULL,   -- e.g. 'section', 'status', 'work_category'
    code            VARCHAR(80)  NOT NULL,   -- machine code, never changes
    label           VARCHAR(200) NOT NULL,   -- displayed text, admin can edit
    is_active       BOOLEAN      NOT NULL DEFAULT TRUE,
    is_system       BOOLEAN      NOT NULL DEFAULT FALSE,  -- TRUE = cannot be deleted
    sort_override   INTEGER      NULL,       -- NULL = sort alphabetically by label
    created_by      BIGINT       NULL,
    created_at      TIMESTAMP    NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMP    NOT NULL DEFAULT NOW(),
    UNIQUE (group_key, code)
);

CREATE INDEX IF NOT EXISTS idx_ddm_group_key        ON dropdown_master(group_key);
CREATE INDEX IF NOT EXISTS idx_ddm_group_active     ON dropdown_master(group_key, is_active);
CREATE INDEX IF NOT EXISTS idx_ddm_code             ON dropdown_master(code);

-- -----------------------------------------------------------------------
-- 2. AUTO-UPDATE updated_at
-- -----------------------------------------------------------------------
DROP TRIGGER IF EXISTS trg_dropdown_master_updated_at ON dropdown_master;
CREATE TRIGGER trg_dropdown_master_updated_at
    BEFORE UPDATE ON dropdown_master
    FOR EACH ROW EXECUTE FUNCTION fn_set_updated_at();

-- -----------------------------------------------------------------------
-- 3. SEED DATA
-- All 8 dropdown groups identified in the Work Ledger form.
-- is_system=TRUE items cannot be deleted by admin (only label editable).
-- Sorted alphabetically by label within each group (default behavior).
-- -----------------------------------------------------------------------

-- GROUP: section
INSERT INTO dropdown_master (group_key, code, label, is_system) VALUES
    ('section', 'ELECTRICAL',  'Electrical',  TRUE),
    ('section', 'GENERAL',     'General',     TRUE),
    ('section', 'MECHANICAL',  'Mechanical',  TRUE)
ON CONFLICT (group_key, code) DO NOTHING;

-- GROUP: work_status
INSERT INTO dropdown_master (group_key, code, label, is_system) VALUES
    ('work_status', 'CLOSED',   'Closed',   TRUE),
    ('work_status', 'OPEN',     'Open',     TRUE),
    ('work_status', 'PENDING',  'Pending',  TRUE)
ON CONFLICT (group_key, code) DO NOTHING;

-- GROUP: work_category  (mirrors work_category_master, kept in sync)
INSERT INTO dropdown_master (group_key, code, label, is_system) VALUES
    ('work_category', 'ACHIEVEMENT',                'Achievement',                         TRUE),
    ('work_category', 'COMPLAINT_LETTER_TO_FIRM',   'Complaint Letter to Firm',            TRUE),
    ('work_category', 'DEVELOPMENT_PO',             'Development PO',                      TRUE),
    ('work_category', 'DISPATCH_CLEARANCE_PROTOTYPE','Dispatch Clearance for Prototype',   TRUE),
    ('work_category', 'DRAWING_MODIFICATION_OR_NEW','Modification in Drawing / New Drawing',TRUE),
    ('work_category', 'ELIGIBILITY_CRITERIA_REVISION','Eligibility Criteria Revision',     TRUE),
    ('work_category', 'LETTER_TO_RDSO_CLW_BLW_ICF', 'Letter to RDSO / CLW / BLW / ICF',  TRUE),
    ('work_category', 'MISC',                        'Miscellaneous',                      TRUE),
    ('work_category', 'NEW_INNOVATION',              'New Innovation',                     TRUE),
    ('work_category', 'PROTOTYPE_INSPECTION',        'Prototype Inspection',               TRUE),
    ('work_category', 'SHOP_VISIT',                  'Shop Visit',                        TRUE),
    ('work_category', 'SOURCE_DEVELOPMENT',          'Source Development',                 TRUE),
    ('work_category', 'SPECIFICATION_MODIFICATION',  'Modification in Specification',      TRUE),
    ('work_category', 'SPECIFICATION_STUDIED',       'Specification Studied',              TRUE),
    ('work_category', 'TECHNICAL_CLARIFICATION',     'Technical Clarification',            TRUE),
    ('work_category', 'TECHNICAL_EVALUATION',        'Technical Evaluation',               TRUE),
    ('work_category', 'TENDER_CASE_FILING',          'Tender Case Filing of Documents',    TRUE),
    ('work_category', 'VISIT_TO_FIRM_PU_ZR',         'Visit to Firm / PU / ZR',            TRUE)
ON CONFLICT (group_key, code) DO NOTHING;

-- GROUP: inspection_result  (used in Prototype Inspection dynamic fields)
INSERT INTO dropdown_master (group_key, code, label, is_system) VALUES
    ('inspection_result', 'APPROVED',           'Approved',           TRUE),
    ('inspection_result', 'CONDITIONALLY_APPROVED', 'Conditionally Approved', TRUE),
    ('inspection_result', 'FAILED',             'Failed',             TRUE),
    ('inspection_result', 'PENDING_REPORT',     'Pending Report',     TRUE)
ON CONFLICT (group_key, code) DO NOTHING;

-- GROUP: concerned_officer  (non-system – admin can manage fully)
-- Initially empty; admin adds officers from admin panel.
-- Example seed shown for reference:
-- INSERT INTO dropdown_master (group_key, code, label, is_system) VALUES
--     ('concerned_officer', 'OFF_001', 'Shri A.K. Gupta (DyCME/LDO)', FALSE);

-- GROUP: engineer_staff  (non-system – admin populates)
-- Initially empty; populated from user/staff master by admin.

-- GROUP: pl_number_prefix  (non-system – admin manages loco PL prefix codes)
INSERT INTO dropdown_master (group_key, code, label, is_system) VALUES
    ('pl_number_prefix', '38100000', '38100000 – WAG9 Loco',   FALSE),
    ('pl_number_prefix', '38110000', '38110000 – WAP7 Loco',   FALSE),
    ('pl_number_prefix', '38120000', '38120000 – DETC/MEMU',   FALSE),
    ('pl_number_prefix', '38130000', '38130000 – DEMU',        FALSE)
ON CONFLICT (group_key, code) DO NOTHING;

-- GROUP: loco_type  (for reference / filtering)
INSERT INTO dropdown_master (group_key, code, label, is_system) VALUES
    ('loco_type', 'DEMU',  'DEMU',  FALSE),
    ('loco_type', 'DETC',  'DETC',  FALSE),
    ('loco_type', 'MEMU',  'MEMU',  FALSE),
    ('loco_type', 'WAG9',  'WAG9',  FALSE),
    ('loco_type', 'WAP7',  'WAP7',  FALSE)
ON CONFLICT (group_key, code) DO NOTHING;

-- -----------------------------------------------------------------------
-- 4. ADMIN AUDIT LOG for dropdown changes
-- -----------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS dropdown_audit_log (
    log_id      BIGSERIAL   PRIMARY KEY,
    dropdown_id BIGINT      NOT NULL,
    group_key   VARCHAR(80) NOT NULL,
    code        VARCHAR(80) NOT NULL,
    action      VARCHAR(20) NOT NULL,  -- CREATED / UPDATED / DEACTIVATED / DELETED
    old_label   VARCHAR(200) NULL,
    new_label   VARCHAR(200) NULL,
    changed_by  BIGINT      NOT NULL,
    changed_at  TIMESTAMP   NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_ddal_dropdown_id ON dropdown_audit_log(dropdown_id);
CREATE INDEX IF NOT EXISTS idx_ddal_group_key   ON dropdown_audit_log(group_key);

-- -----------------------------------------------------------------------
-- 5. REPORTING VIEW: all active dropdowns sorted alphabetically
-- -----------------------------------------------------------------------
CREATE OR REPLACE VIEW vw_active_dropdowns AS
SELECT
    id,
    group_key,
    code,
    label,
    is_system,
    sort_override,
    CASE
        WHEN sort_override IS NOT NULL THEN sort_override
        ELSE ROW_NUMBER() OVER (PARTITION BY group_key ORDER BY label ASC)
    END AS effective_sort
FROM dropdown_master
WHERE is_active = TRUE
ORDER BY group_key, effective_sort, label;

-- =============================================================================
-- END: sql/005_dropdown_master.sql
-- =============================================================================

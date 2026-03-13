-- =============================================================================
-- FILE: sql/007_custom_fields.sql
-- SPRINT 1 | FEATURE #9: Custom Fields per Document Type
-- PURPOSE : Allow admin to define per-document-type metadata fields.
--           Each document instance can then store field_name/field_value pairs.
--           Pattern mirrors work_ledger_detail already proven in WorkLedger.
-- DEPENDS : edms_document_type, edms_document (Phase 1 schema)
-- MIGRATION: Run after 006_fix_fk_constraints.sql
-- =============================================================================

-- ---- Table 1: Field definitions per document type (admin-managed) ----
CREATE TABLE IF NOT EXISTS edms_custom_field_definition (
    id              BIGSERIAL PRIMARY KEY,
    document_type_id BIGINT NOT NULL
                        REFERENCES edms_document_type(id) ON DELETE CASCADE,
    field_name      VARCHAR(80)  NOT NULL,
    field_label     VARCHAR(200) NOT NULL,
    field_type      VARCHAR(20)  NOT NULL DEFAULT 'text'
                        CHECK (field_type IN ('text','number','date','select','boolean')),
    select_options  TEXT         NULL,   -- comma-separated options when field_type='select'
    is_required     BOOLEAN      NOT NULL DEFAULT FALSE,
    sort_order      INT          NOT NULL DEFAULT 0,
    is_active       BOOLEAN      NOT NULL DEFAULT TRUE,
    created_at      TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    UNIQUE (document_type_id, field_name)
);

COMMENT ON TABLE  edms_custom_field_definition IS 'Admin-defined metadata fields per document type (e.g. Specification No, Clause, Issue Authority).';
COMMENT ON COLUMN edms_custom_field_definition.select_options IS 'Comma-separated option list when field_type=select. Example: RDSO,CLW,BLW,ICF';

CREATE INDEX IF NOT EXISTS idx_cfd_doctype  ON edms_custom_field_definition(document_type_id);
CREATE INDEX IF NOT EXISTS idx_cfd_active   ON edms_custom_field_definition(document_type_id, is_active);

-- ---- Table 2: Actual field values per document instance ----
CREATE TABLE IF NOT EXISTS edms_document_custom_field (
    id              BIGSERIAL PRIMARY KEY,
    document_id     BIGINT NOT NULL
                        REFERENCES edms_document(id) ON DELETE CASCADE,
    definition_id   BIGINT NOT NULL
                        REFERENCES edms_custom_field_definition(id) ON DELETE RESTRICT,
    field_value     TEXT   NULL,
    updated_by      BIGINT NULL REFERENCES core_user(id) ON DELETE SET NULL,
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (document_id, definition_id)
);

COMMENT ON TABLE edms_document_custom_field IS 'Per-document custom field values, linked to admin-defined field definitions.';

CREATE INDEX IF NOT EXISTS idx_dcf_document    ON edms_document_custom_field(document_id);
CREATE INDEX IF NOT EXISTS idx_dcf_definition  ON edms_document_custom_field(definition_id);
-- trigram index for value search
CREATE INDEX IF NOT EXISTS idx_dcf_value_trgm  ON edms_document_custom_field USING GIN (field_value gin_trgm_ops);

-- =============================================================================
-- FILE: sql/008_correspondents.sql
-- SPRINT 1 | FEATURE #14: Correspondent Tracking
-- PURPOSE : Track organisations that issue or receive EDMS documents.
--           Replaces free-text eoffice_file_number for sender/recipient info.
-- DEPENDS : edms_document (Phase 1), core_user
-- MIGRATION: Run after 007_custom_fields.sql
-- =============================================================================

-- ---- Table 1: Correspondent master ----
CREATE TABLE IF NOT EXISTS correspondent (
    id          BIGSERIAL PRIMARY KEY,
    name        VARCHAR(300) NOT NULL,
    short_code  VARCHAR(30)  NOT NULL UNIQUE,
    org_type    VARCHAR(20)  NOT NULL DEFAULT 'OTHER'
                    CHECK (org_type IN ('RDSO','CLW','BLW','ICF','ZR','HQ','VENDOR','CONTRACTOR','OTHER')),
    address     TEXT         NULL,
    email       VARCHAR(200) NULL,
    is_active   BOOLEAN      NOT NULL DEFAULT TRUE,
    created_by  BIGINT       NULL REFERENCES core_user(id) ON DELETE SET NULL,
    created_at  TIMESTAMPTZ  NOT NULL DEFAULT NOW()
);

COMMENT ON TABLE correspondent IS 'Master list of organisations — RDSO, CLW, BLW, Zonal Railways, vendors — that issue or receive documents.';

CREATE INDEX IF NOT EXISTS idx_correspondent_type    ON correspondent(org_type);
CREATE INDEX IF NOT EXISTS idx_correspondent_active  ON correspondent(is_active);

-- ---- Seed data: common Indian Railways correspondents ----
INSERT INTO correspondent (name, short_code, org_type) VALUES
    ('Research Designs and Standards Organisation',         'RDSO',   'RDSO'),
    ('Chittaranjan Locomotive Works',                      'CLW',    'CLW'),
    ('Banaras Locomotive Works',                           'BLW',    'BLW'),
    ('Integral Coach Factory',                             'ICF',    'ICF'),
    ('Rail Wheel Factory',                                 'RWF',    'HQ'),
    ('Railway Board (Ministry of Railways)',               'RLY-BD', 'HQ'),
    ('North Central Railway Headquarters',                 'NCR-HQ', 'ZR'),
    ('Northern Railway Headquarters',                      'NR-HQ',  'ZR'),
    ('Central Railway Headquarters',                       'CR-HQ',  'ZR'),
    ('Western Railway Headquarters',                       'WR-HQ',  'ZR'),
    ('South Central Railway Headquarters',                 'SCR-HQ', 'ZR'),
    ('ABB India Limited',                                  'ABB',    'VENDOR'),
    ('Medha Servo Drives',                                 'MEDHA',  'VENDOR'),
    ('BHEL (Bhopal)',                                      'BHEL',   'VENDOR')
ON CONFLICT (short_code) DO NOTHING;

-- ---- Table 2: Document-Correspondent link ----
CREATE TABLE IF NOT EXISTS document_correspondent_link (
    id                BIGSERIAL PRIMARY KEY,
    document_id       BIGINT      NOT NULL REFERENCES edms_document(id) ON DELETE CASCADE,
    correspondent_id  BIGINT      NOT NULL REFERENCES correspondent(id) ON DELETE RESTRICT,
    reference_number  VARCHAR(200) NULL,   -- e.g. RDSO letter number
    reference_date    DATE         NULL,
    link_type         VARCHAR(20)  NOT NULL DEFAULT 'ISSUED_BY'
                          CHECK (link_type IN ('ISSUED_BY','ADDRESSED_TO','CC','APPROVED_BY','CONSULTED')),
    remarks           TEXT         NULL,
    created_by        BIGINT       NULL REFERENCES core_user(id) ON DELETE SET NULL,
    created_at        TIMESTAMPTZ  NOT NULL DEFAULT NOW()
);

COMMENT ON TABLE document_correspondent_link IS 'Links documents to the organisations that issued, received, or approved them.';

CREATE INDEX IF NOT EXISTS idx_dcl_document       ON document_correspondent_link(document_id);
CREATE INDEX IF NOT EXISTS idx_dcl_correspondent  ON document_correspondent_link(correspondent_id);
CREATE INDEX IF NOT EXISTS idx_dcl_refno          ON document_correspondent_link(reference_number);

-- =============================================================================
-- FILE: sql/017_sharelinks.sql
-- SPRINT 7 | Shareable links table
-- =============================================================================
CREATE TABLE IF NOT EXISTS sharelink (
    id                   BIGSERIAL    PRIMARY KEY,
    token                VARCHAR(64)  NOT NULL UNIQUE,
    document_id          BIGINT       NOT NULL REFERENCES edms_document(id) ON DELETE CASCADE,
    revision_id          BIGINT       NULL     REFERENCES edms_revision(id) ON DELETE SET NULL,
    access_level         VARCHAR(20)  NOT NULL DEFAULT 'VIEW_FILE'
                             CHECK (access_level IN ('VIEW_METADATA','VIEW_FILE')),
    label                VARCHAR(200) NOT NULL DEFAULT '',
    password_hash        VARCHAR(128) NOT NULL DEFAULT '',
    expires_at           TIMESTAMPTZ  NOT NULL,
    is_active            BOOLEAN      NOT NULL DEFAULT TRUE,
    max_uses             INT          NULL,
    use_count            INT          NOT NULL DEFAULT 0,
    rate_limit_per_hour  INT          NOT NULL DEFAULT 20,
    access_log           JSONB        NOT NULL DEFAULT '[]',
    created_by_id        BIGINT       NULL REFERENCES core_user(id) ON DELETE SET NULL,
    created_at           TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    revoked_by_id        BIGINT       NULL REFERENCES core_user(id) ON DELETE SET NULL,
    revoked_at           TIMESTAMPTZ  NULL
);

CREATE INDEX IF NOT EXISTS idx_sharelink_token    ON sharelink(token);
CREATE INDEX IF NOT EXISTS idx_sharelink_doc      ON sharelink(document_id);
CREATE INDEX IF NOT EXISTS idx_sharelink_expires  ON sharelink(expires_at) WHERE is_active = TRUE;

COMMENT ON TABLE sharelink IS
    'Token-based public document share links. No auth required on /s/{token}/ routes.';

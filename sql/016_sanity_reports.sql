-- =============================================================================
-- FILE: sql/016_sanity_reports.sql
-- SPRINT 6 | Sanity Check report store
-- =============================================================================
CREATE TABLE IF NOT EXISTS sanity_report (
    id               BIGSERIAL   PRIMARY KEY,
    run_by_id        BIGINT      NULL REFERENCES core_user(id) ON DELETE SET NULL,
    ran_at           TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    total_issues     INT         NOT NULL DEFAULT 0,
    error_count      INT         NOT NULL DEFAULT 0,
    warning_count    INT         NOT NULL DEFAULT 0,
    info_count       INT         NOT NULL DEFAULT 0,
    issues           JSONB       NOT NULL DEFAULT '[]',
    stale_draft_days INT         NOT NULL DEFAULT 90
);

CREATE INDEX IF NOT EXISTS idx_sanity_ran_at ON sanity_report(ran_at DESC);

COMMENT ON TABLE sanity_report IS
    'Snapshot of each sanity check run. Issues stored as JSONB array.';

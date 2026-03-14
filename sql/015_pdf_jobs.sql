-- =============================================================================
-- FILE: sql/015_pdf_jobs.sql
-- SPRINT 6 | PDF Tools job queue table
-- =============================================================================
CREATE TABLE IF NOT EXISTS pdf_job (
    id                 BIGSERIAL    PRIMARY KEY,
    operation          VARCHAR(10)  NOT NULL
                           CHECK (operation IN ('MERGE','SPLIT','ROTATE','EXTRACT')),
    status             VARCHAR(10)  NOT NULL DEFAULT 'QUEUED'
                           CHECK (status IN ('QUEUED','RUNNING','DONE','FAILED')),
    input_files        JSONB        NOT NULL DEFAULT '[]',
    params             JSONB        NOT NULL DEFAULT '{}',
    output_files       JSONB        NOT NULL DEFAULT '[]',
    error_message      TEXT         NOT NULL DEFAULT '',
    created_by_id      BIGINT       NULL REFERENCES core_user(id) ON DELETE SET NULL,
    linked_revision_id BIGINT       NULL REFERENCES edms_revision(id) ON DELETE SET NULL,
    created_at         TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    completed_at       TIMESTAMPTZ  NULL
);

CREATE INDEX IF NOT EXISTS idx_pdf_job_user   ON pdf_job(created_by_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_pdf_job_status ON pdf_job(status);

COMMENT ON TABLE pdf_job IS
    'Async PDF operation jobs (merge/split/rotate/extract). Output stored in MEDIA_ROOT/pdf_ops/.';

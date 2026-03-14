-- =============================================================================
-- FILE: sql/009_document_notes.sql
-- SPRINT 1 | FEATURE #12: Document Notes & Annotations
-- PURPOSE : Allow engineers and section heads to attach review comments,
--           queries, or observations to a document revision.
--           Notes are append-only (no DELETE for audit safety).
--           Resolved notes show who resolved them and when.
-- DEPENDS : edms_document, edms_revision, core_user
-- MIGRATION: Run after 008_correspondents.sql
-- =============================================================================

CREATE TABLE IF NOT EXISTS document_note (
    id              BIGSERIAL PRIMARY KEY,
    document_id     BIGINT       NOT NULL REFERENCES edms_document(id) ON DELETE CASCADE,
    revision_id     BIGINT       NULL     REFERENCES edms_revision(id) ON DELETE SET NULL,
    note_type       VARCHAR(20)  NOT NULL DEFAULT 'OBSERVATION'
                        CHECK (note_type IN ('REVIEW','QUERY','OBSERVATION','INFO','ACTION_REQUIRED')),
    note_text       TEXT         NOT NULL,
    is_resolved     BOOLEAN      NOT NULL DEFAULT FALSE,
    resolved_by     BIGINT       NULL REFERENCES core_user(id) ON DELETE SET NULL,
    resolved_at     TIMESTAMPTZ  NULL,
    resolution_note TEXT         NULL,
    created_by      BIGINT       NOT NULL REFERENCES core_user(id) ON DELETE RESTRICT,
    created_at      TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ  NOT NULL DEFAULT NOW()
);

COMMENT ON TABLE  document_note IS 'Append-only review comments and observations per document/revision. No DELETE allowed — notes are audit evidence.';
COMMENT ON COLUMN document_note.revision_id IS 'NULL means note is on the document in general; non-NULL pins note to a specific revision.';
COMMENT ON COLUMN document_note.note_type   IS 'REVIEW=formal review comment, QUERY=question needing reply, OBSERVATION=informal note, INFO=reference info, ACTION_REQUIRED=pending action item.';

-- Protect against DELETE on this table (audit safety)
CREATE OR REPLACE RULE no_delete_document_note AS
    ON DELETE TO document_note DO INSTEAD NOTHING;

CREATE INDEX IF NOT EXISTS idx_dn_document    ON document_note(document_id);
CREATE INDEX IF NOT EXISTS idx_dn_revision    ON document_note(revision_id);
CREATE INDEX IF NOT EXISTS idx_dn_created_by  ON document_note(created_by);
CREATE INDEX IF NOT EXISTS idx_dn_unresolved  ON document_note(document_id, is_resolved) WHERE is_resolved = FALSE;

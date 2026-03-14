-- =============================================================================
-- FILE: sql/012_approval_engine.sql
-- SPRINT 4 | FEATURE: Document Approval Workflow Engine
-- PURPOSE : Stores approval chain templates and per-document approval runs.
--           An ApprovalChain defines an ordered sequence of roles/users.
--           An ApprovalRequest is one execution of a chain against a Revision.
--           An ApprovalVote records each individual approver's decision.
-- DEPENDS : edms_document, edms_revision, core_user
-- MIGRATION: Run after 011_saved_views.sql
-- =============================================================================

-- ---- Chain template ---------------------------------------------------------
CREATE TABLE IF NOT EXISTS workflow_approval_chain (
    id           BIGSERIAL    PRIMARY KEY,
    name         VARCHAR(200) NOT NULL,
    document_type_id BIGINT   NULL REFERENCES edms_document_type(id) ON DELETE SET NULL,
    -- NULL document_type means the chain is universal (any doc type)
    is_active    BOOLEAN      NOT NULL DEFAULT TRUE,
    created_by_id BIGINT      NULL REFERENCES core_user(id) ON DELETE SET NULL,
    created_at   TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    updated_at   TIMESTAMPTZ  NOT NULL DEFAULT NOW()
);

COMMENT ON TABLE workflow_approval_chain IS
    'Named approval chain template. Steps define the ordered approver sequence.';

-- ---- Chain steps (ordered approvers) ---------------------------------------
CREATE TABLE IF NOT EXISTS workflow_approval_step (
    id          BIGSERIAL    PRIMARY KEY,
    chain_id    BIGINT       NOT NULL REFERENCES workflow_approval_chain(id) ON DELETE CASCADE,
    step_order  INT          NOT NULL DEFAULT 0,
    label       VARCHAR(120) NOT NULL,              -- e.g. "Checker", "Section Engineer"
    role        VARCHAR(50)  NULL,                  -- optional role constraint
    assigned_user_id BIGINT  NULL REFERENCES core_user(id) ON DELETE SET NULL,
    -- Either role OR assigned_user must be set (enforced at app layer)
    due_days    INT          NOT NULL DEFAULT 3,    -- SLA days from step activation
    is_optional BOOLEAN      NOT NULL DEFAULT FALSE,
    UNIQUE (chain_id, step_order)
);

COMMENT ON TABLE workflow_approval_step IS
    'Ordered approver step within an ApprovalChain.';

-- ---- Approval request (one run of a chain on a revision) -------------------
CREATE TABLE IF NOT EXISTS workflow_approval_request (
    id           BIGSERIAL    PRIMARY KEY,
    chain_id     BIGINT       NOT NULL REFERENCES workflow_approval_chain(id),
    revision_id  BIGINT       NOT NULL REFERENCES edms_revision(id),
    status       VARCHAR(20)  NOT NULL DEFAULT 'PENDING'
                     CHECK (status IN ('PENDING','IN_REVIEW','APPROVED','REJECTED','WITHDRAWN')),
    current_step INT          NOT NULL DEFAULT 0,
    initiated_by_id BIGINT   NULL REFERENCES core_user(id) ON DELETE SET NULL,
    initiated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    completed_at TIMESTAMPTZ NULL,
    remarks      TEXT         NOT NULL DEFAULT '',
    UNIQUE (revision_id, chain_id)  -- one active run per chain per revision
);

CREATE INDEX IF NOT EXISTS idx_apr_status   ON workflow_approval_request(status);
CREATE INDEX IF NOT EXISTS idx_apr_revision ON workflow_approval_request(revision_id);

COMMENT ON TABLE workflow_approval_request IS
    'One execution of an ApprovalChain on a specific Revision.';

-- ---- Approval votes (one row per step per request) -------------------------
CREATE TABLE IF NOT EXISTS workflow_approval_vote (
    id          BIGSERIAL    PRIMARY KEY,
    request_id  BIGINT       NOT NULL REFERENCES workflow_approval_request(id) ON DELETE CASCADE,
    step_id     BIGINT       NOT NULL REFERENCES workflow_approval_step(id),
    voted_by_id BIGINT       NULL REFERENCES core_user(id) ON DELETE SET NULL,
    vote        VARCHAR(15)  NOT NULL
                    CHECK (vote IN ('APPROVED','REJECTED','DELEGATED','RETURNED')),
    comment     TEXT         NOT NULL DEFAULT '',
    voted_at    TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    UNIQUE (request_id, step_id)
);

CREATE INDEX IF NOT EXISTS idx_vote_request ON workflow_approval_vote(request_id);
CREATE INDEX IF NOT EXISTS idx_vote_voter   ON workflow_approval_vote(voted_by_id);

COMMENT ON TABLE workflow_approval_vote IS
    'Individual approver vote within an ApprovalRequest.';

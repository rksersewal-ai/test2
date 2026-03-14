-- =============================================================================
-- FILE: sql/014_ml_classifier.sql
-- SPRINT 5 | ML Metadata Classifier tables
-- DEPENDS : edms_document, core_user
-- =============================================================================

CREATE TABLE IF NOT EXISTS ml_classifier_model (
    id             BIGSERIAL    PRIMARY KEY,
    target         VARCHAR(30)  NOT NULL,
    version        INT          NOT NULL DEFAULT 1,
    model_path     VARCHAR(500) NOT NULL,
    label_path     VARCHAR(500) NOT NULL,
    accuracy       FLOAT        NULL,
    training_docs  INT          NULL,
    is_active      BOOLEAN      NOT NULL DEFAULT TRUE,
    trained_by_id  BIGINT       NULL REFERENCES core_user(id) ON DELETE SET NULL,
    trained_at     TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    notes          TEXT         NOT NULL DEFAULT '',
    UNIQUE (target, version)
);

CREATE INDEX IF NOT EXISTS idx_clf_target_active
    ON ml_classifier_model(target, is_active);

COMMENT ON TABLE ml_classifier_model IS
    'Versioned ML classifier artefact registry. One active row per target.';

-- -----------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS ml_classification_result (
    id              BIGSERIAL    PRIMARY KEY,
    document_id     BIGINT       NOT NULL REFERENCES edms_document(id) ON DELETE CASCADE,
    classifier_id   BIGINT       NULL     REFERENCES ml_classifier_model(id) ON DELETE SET NULL,
    target          VARCHAR(30)  NOT NULL,
    predictions     JSONB        NOT NULL DEFAULT '[]',
    top_label       VARCHAR(200) NOT NULL DEFAULT '',
    top_label_id    INT          NULL,
    top_confidence  FLOAT        NULL,
    outcome         VARCHAR(15)  NOT NULL DEFAULT 'PENDING'
                        CHECK (outcome IN ('PENDING','ACCEPTED','OVERRIDDEN','REJECTED')),
    reviewed_by_id  BIGINT       NULL REFERENCES core_user(id) ON DELETE SET NULL,
    reviewed_at     TIMESTAMPTZ  NULL,
    created_at      TIMESTAMPTZ  NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_clf_result_doc_target
    ON ml_classification_result(document_id, target);
CREATE INDEX IF NOT EXISTS idx_clf_result_outcome
    ON ml_classification_result(outcome);

COMMENT ON TABLE ml_classification_result IS
    'Per-document ML prediction audit trail with user review outcome.';

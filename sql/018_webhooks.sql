-- =============================================================================
-- FILE: sql/018_webhooks.sql
-- SPRINT 7 | Webhook endpoint registry + delivery log
-- =============================================================================

CREATE TABLE IF NOT EXISTS webhook_endpoint (
    id              BIGSERIAL    PRIMARY KEY,
    name            VARCHAR(200) NOT NULL,
    url             VARCHAR(500) NOT NULL,
    secret          VARCHAR(128) NOT NULL,
    events          JSONB        NOT NULL DEFAULT '[]',
    is_active       BOOLEAN      NOT NULL DEFAULT TRUE,
    timeout_seconds INT          NOT NULL DEFAULT 10,
    max_retries     INT          NOT NULL DEFAULT 5,
    created_by_id   BIGINT       NULL REFERENCES core_user(id) ON DELETE SET NULL,
    created_at      TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ  NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS webhook_delivery (
    id              BIGSERIAL   PRIMARY KEY,
    endpoint_id     BIGINT      NOT NULL REFERENCES webhook_endpoint(id) ON DELETE CASCADE,
    event_name      VARCHAR(100) NOT NULL,
    payload         JSONB       NOT NULL DEFAULT '{}',
    status          VARCHAR(10) NOT NULL DEFAULT 'PENDING'
                        CHECK (status IN ('PENDING','SUCCESS','FAILED','RETRYING','ABANDONED')),
    attempt_count   INT         NOT NULL DEFAULT 0,
    response_status INT         NULL,
    response_body   TEXT        NOT NULL DEFAULT '',
    error_message   TEXT        NOT NULL DEFAULT '',
    next_retry_at   TIMESTAMPTZ NULL,
    delivered_at    TIMESTAMPTZ NULL,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_wh_delivery_status    ON webhook_delivery(status, next_retry_at);
CREATE INDEX IF NOT EXISTS idx_wh_delivery_endpoint  ON webhook_delivery(endpoint_id, event_name);

COMMENT ON TABLE webhook_endpoint IS 'Registered external HTTP endpoints for EDMS event webhooks.';
COMMENT ON TABLE webhook_delivery IS 'Delivery attempt log per event per endpoint.';

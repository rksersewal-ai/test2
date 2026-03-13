-- =============================================================================
-- FILE: sql/013_notifications.sql
-- SPRINT 4 | FEATURE: In-App Notifications
-- PURPOSE : Per-user notification inbox. Notifications are created by Django
--           signals (approval events, overdue reminders, OCR completions).
--           SSE endpoint polls this table. No WebSocket needed.
-- DEPENDS : core_user
-- MIGRATION: Run after 012_approval_engine.sql
-- =============================================================================

CREATE TABLE IF NOT EXISTS notification_inbox (
    id           BIGSERIAL    PRIMARY KEY,
    user_id      BIGINT       NOT NULL REFERENCES core_user(id) ON DELETE CASCADE,
    kind         VARCHAR(40)  NOT NULL DEFAULT 'INFO'
                     CHECK (kind IN (
                         'INFO','SUCCESS','WARNING','ERROR',
                         'APPROVAL_REQUESTED','APPROVAL_VOTED',
                         'APPROVAL_APPROVED','APPROVAL_REJECTED',
                         'OVERDUE_WORK','OCR_COMPLETE','OCR_FAILED',
                         'DOCUMENT_PUBLISHED','MENTION'
                     )),
    title        VARCHAR(300) NOT NULL,
    body         TEXT         NOT NULL DEFAULT '',
    action_url   VARCHAR(500) NOT NULL DEFAULT '',  -- frontend route to navigate to
    is_read      BOOLEAN      NOT NULL DEFAULT FALSE,
    created_at   TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    expires_at   TIMESTAMPTZ  NULL     -- NULL = never expire
);

CREATE INDEX IF NOT EXISTS idx_notif_user_unread
    ON notification_inbox(user_id, is_read, created_at DESC)
    WHERE is_read = FALSE;

CREATE INDEX IF NOT EXISTS idx_notif_user_all
    ON notification_inbox(user_id, created_at DESC);

COMMENT ON TABLE notification_inbox IS
    'Per-user notification inbox. Polled by SSE endpoint every 15s.';

-- Auto-expire old read notifications after 30 days (pg_cron or Celery beat)
-- DELETE FROM notification_inbox WHERE is_read AND created_at < NOW() - INTERVAL '30 days';

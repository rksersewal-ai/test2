-- =============================================================================
-- FILE: sql/019_totp_fields.sql
-- SPRINT 8 | TOTP / 2FA fields on core_user
-- Run AFTER Sprint 7 migrations.
-- =============================================================================
ALTER TABLE core_user
    ADD COLUMN IF NOT EXISTS totp_secret       VARCHAR(64)  NOT NULL DEFAULT '',
    ADD COLUMN IF NOT EXISTS totp_enabled      BOOLEAN      NOT NULL DEFAULT FALSE,
    ADD COLUMN IF NOT EXISTS totp_backup_codes JSONB        NOT NULL DEFAULT '[]',
    ADD COLUMN IF NOT EXISTS totp_enforced_at  TIMESTAMPTZ  NULL;

COMMENT ON COLUMN core_user.totp_secret       IS 'Base32 TOTP secret. Empty = not enrolled.';
COMMENT ON COLUMN core_user.totp_enabled      IS 'True after first successful TOTP verification at setup.';
COMMENT ON COLUMN core_user.totp_backup_codes IS 'SHA-256 hashes of 8 one-time backup codes.';
COMMENT ON COLUMN core_user.totp_enforced_at  IS 'Timestamp when 2FA was activated for this user.';

CREATE INDEX IF NOT EXISTS idx_user_totp_enabled
    ON core_user(totp_enabled) WHERE totp_enabled = TRUE;

-- =============================================================================
-- FILE: sql/006_fix_fk_constraints.sql
-- FIX (#4): Add proper FK constraints to dropdown_master and dropdown_audit_log.
--           created_by / changed_by reference core_user(id) ON DELETE SET NULL.
-- FIX (#11): Remove 'section' group from dropdown_master since core_section
--            table is the authoritative source. Prevents dual-maintenance.
-- FIX (#7): Create per-year work_code sequences (2025 and 2026 bootstrapped).
-- =============================================================================

-- ---- FIX (#4): Add FK from dropdown_master.created_by → core_user ----
ALTER TABLE dropdown_master
    ADD COLUMN IF NOT EXISTS created_by_user_id BIGINT NULL
        REFERENCES core_user(id) ON DELETE SET NULL;

-- Migrate existing raw integer into FK column
UPDATE dropdown_master SET created_by_user_id = created_by WHERE created_by IS NOT NULL;

-- Drop the old raw integer column
ALTER TABLE dropdown_master DROP COLUMN IF EXISTS created_by;
ALTER TABLE dropdown_master RENAME COLUMN created_by_user_id TO created_by;

-- ---- FIX (#4): Add FK from dropdown_audit_log.changed_by → core_user ----
ALTER TABLE dropdown_audit_log
    ADD COLUMN IF NOT EXISTS changed_by_user_id BIGINT NULL
        REFERENCES core_user(id) ON DELETE SET NULL;

UPDATE dropdown_audit_log SET changed_by_user_id = changed_by;

ALTER TABLE dropdown_audit_log DROP COLUMN IF EXISTS changed_by;
ALTER TABLE dropdown_audit_log RENAME COLUMN changed_by_user_id TO changed_by;

-- ---- FIX (#11): Remove duplicate 'section' group from dropdown_master ----
-- Section data is owned by core_section table, not dropdown_master.
-- The DropdownSelect component for 'section' should call /api/core/sections/ instead.
DELETE FROM dropdown_master WHERE group_key = 'section';

-- ---- FIX (#5): Revision prepared_by / approved_by FK migration ----
-- Add FK columns alongside the old CharField columns
ALTER TABLE edms_revision
    ADD COLUMN IF NOT EXISTS prepared_by_id BIGINT NULL REFERENCES core_user(id) ON DELETE SET NULL,
    ADD COLUMN IF NOT EXISTS approved_by_id BIGINT NULL REFERENCES core_user(id) ON DELETE SET NULL;

-- NOTE: After running this script, run Django migration for Revision model:
--   python manage.py makemigrations edms
--   python manage.py migrate edms
-- The old prepared_by / approved_by CharField columns will be removed by the migration.

-- ---- FIX (#7): Bootstrap per-year work_code sequences ----
DO $$
DECLARE yr INT;
BEGIN
    FOR yr IN 2025..2030 LOOP
        IF NOT EXISTS (
            SELECT 1 FROM pg_sequences WHERE sequencename = 'wl_work_code_' || yr || '_seq'
        ) THEN
            EXECUTE 'CREATE SEQUENCE wl_work_code_' || yr || '_seq START 1 INCREMENT 1 NO CYCLE';
        END IF;
    END LOOP;
END
$$;

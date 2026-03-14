-- =============================================================================
-- FILE: sql/006_fixes.sql
-- PURPOSE: Apply all structural DB fixes identified in repo weak point analysis
-- =============================================================================

-- FIX #4: Add FK constraints to dropdown_master and dropdown_audit_log
-- (core_user table must exist before running this)
ALTER TABLE dropdown_master
    DROP COLUMN IF EXISTS created_by,
    ADD COLUMN created_by BIGINT NULL REFERENCES core_user(id) ON DELETE SET NULL;

ALTER TABLE dropdown_audit_log
    DROP COLUMN IF EXISTS changed_by,
    ADD COLUMN changed_by BIGINT NULL REFERENCES core_user(id) ON DELETE SET NULL;

-- FIX #7: Create work_code sequences for current year and next year
-- (repositories.py auto-creates on demand, but pre-seed here for clarity)
CREATE SEQUENCE IF NOT EXISTS wl_work_code_2026_seq START 1 INCREMENT 1 NO CYCLE;
CREATE SEQUENCE IF NOT EXISTS wl_work_code_2027_seq START 1 INCREMENT 1 NO CYCLE;

-- FIX #11: Remove section group from dropdown_master (duplicates core_section table)
-- The Section dropdown is already managed via core.Section model + its own API.
DELETE FROM dropdown_master WHERE group_key = 'section';

-- FIX #5: Migration columns for Revision prepared_by / approved_by FK
-- Run AFTER Django migration: python manage.py makemigrations edms && migrate
-- The Django migration will handle column rename + FK creation.
-- This SQL block is for reference only if using raw SQL migration path:
--
-- ALTER TABLE edms_revision
--     ADD COLUMN prepared_by_id BIGINT NULL REFERENCES core_user(id) ON DELETE SET NULL,
--     ADD COLUMN approved_by_id BIGINT NULL REFERENCES core_user(id) ON DELETE SET NULL;
-- UPDATE edms_revision r
--     SET prepared_by_id = u.id
--     FROM core_user u
--     WHERE u.full_name = r.prepared_by AND r.prepared_by IS NOT NULL;
-- ALTER TABLE edms_revision
--     DROP COLUMN IF EXISTS prepared_by,
--     DROP COLUMN IF EXISTS approved_by;

-- FIX #13: Wrap next_revision_number in SELECT FOR UPDATE on document row
-- (handled in Python services.py - see edms/services.py fix)

-- =============================================================================
-- END: sql/006_fixes.sql
-- =============================================================================

-- =============================================================================
-- FILE: sql/FIX_011_rename_tables.sql
-- Run ONLY if tables were already created with the old names.
-- Safe to run: uses IF EXISTS to skip if already renamed or never existed.
-- =============================================================================

-- Rename Correspondent table
DO $$
BEGIN
    IF EXISTS (SELECT FROM pg_tables WHERE schemaname='public' AND tablename='correspondent')
    AND NOT EXISTS (SELECT FROM pg_tables WHERE schemaname='public' AND tablename='edms_correspondent')
    THEN
        ALTER TABLE correspondent RENAME TO edms_correspondent;
        RAISE NOTICE 'Renamed: correspondent -> edms_correspondent';
    END IF;
END $$;

-- Rename DocumentCorrespondentLink table
DO $$
BEGIN
    IF EXISTS (SELECT FROM pg_tables WHERE schemaname='public' AND tablename='document_correspondent_link')
    AND NOT EXISTS (SELECT FROM pg_tables WHERE schemaname='public' AND tablename='edms_document_correspondent_link')
    THEN
        ALTER TABLE document_correspondent_link RENAME TO edms_document_correspondent_link;
        RAISE NOTICE 'Renamed: document_correspondent_link -> edms_document_correspondent_link';
    END IF;
END $$;

-- Rename DocumentNote table
DO $$
BEGIN
    IF EXISTS (SELECT FROM pg_tables WHERE schemaname='public' AND tablename='document_note')
    AND NOT EXISTS (SELECT FROM pg_tables WHERE schemaname='public' AND tablename='edms_document_note')
    THEN
        ALTER TABLE document_note RENAME TO edms_document_note;
        RAISE NOTICE 'Renamed: document_note -> edms_document_note';
    END IF;
END $$;

SELECT 'FIX_011: Table rename complete.' AS status;

-- Migration 001: Enable PostgreSQL extensions required by PLW EDMS + LDO
-- Run as superuser before Django migrations

CREATE EXTENSION IF NOT EXISTS pg_trgm;        -- Trigram search for OCR text
CREATE EXTENSION IF NOT EXISTS unaccent;       -- Accent-insensitive search
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";    -- UUID generation support

-- Verify
SELECT extname, extversion FROM pg_extension
WHERE extname IN ('pg_trgm', 'unaccent', 'uuid-ossp');

-- =============================================================================
-- FILE: sql/010_search_indexes.sql
-- SPRINT 2 | FEATURE #8: "More Like This" Similarity Search
-- PURPOSE : Enable PostgreSQL trigram similarity search on document metadata
--           and OCR text. pg_trgm is already available in PostgreSQL 15.
--           All indexes are GIN for fast similarity scoring.
-- DEPENDS : edms_document, edms_document_custom_field (007)
-- MIGRATION: Run after 009_document_notes.sql
-- NOTE    : These are advisory CREATE INDEX statements. Django migrations will
--           also manage the ORM-side; these ensure indexes exist on raw SQL runs.
-- =============================================================================

-- Enable extension (idempotent)
CREATE EXTENSION IF NOT EXISTS pg_trgm;

-- Trigram index on document title
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_edms_doc_title_trgm
    ON edms_document USING GIN (title gin_trgm_ops);

-- Trigram index on keywords text blob
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_edms_doc_keywords_trgm
    ON edms_document USING GIN (keywords gin_trgm_ops);

-- Trigram index on document number (for partial-match search)
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_edms_doc_number_trgm
    ON edms_document USING GIN (document_number gin_trgm_ops);

-- Trigram index on eoffice subject
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_edms_doc_subject_trgm
    ON edms_document USING GIN (eoffice_subject gin_trgm_ops);

-- Composite expression index for similarity: title || ' ' || keywords
-- Used by the get_similar_documents() raw SQL query
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_edms_doc_combined_trgm
    ON edms_document USING GIN ((title || ' ' || keywords) gin_trgm_ops);

-- Trigram index on custom field values (from Sprint 1 — verify exists)
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_dcf_value_trgm
    ON edms_document_custom_field USING GIN (field_value gin_trgm_ops);

-- Full-text search vector index on OCR result text (if table exists)
-- Wrapped in DO block for safety in case OCR table isn't yet migrated
DO $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM information_schema.tables
        WHERE table_name = 'ocr_result'
    ) THEN
        EXECUTE $sql$
            CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_ocr_result_text_trgm
                ON ocr_result USING GIN (full_text gin_trgm_ops)
        $sql$;
    END IF;
END;
$$;

COMMENT ON INDEX idx_edms_doc_combined_trgm IS
    'Drives get_similar_documents() similarity scoring in DocumentRepository.';

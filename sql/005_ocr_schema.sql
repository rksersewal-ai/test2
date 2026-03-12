-- Migration 005: OCR queue and result schema indexes

CREATE INDEX IF NOT EXISTS idx_ocr_queue_status_priority ON ocr_queue(status, priority);
CREATE INDEX IF NOT EXISTS idx_ocr_queue_status_queued ON ocr_queue(status, queued_at);

-- Full-text search index on OCR extracted text (GIN for performance)
CREATE INDEX IF NOT EXISTS idx_ocr_result_fulltext_gin ON ocr_result USING gin(to_tsvector('english', full_text));

-- Trigram index for partial-match search on OCR text
CREATE INDEX IF NOT EXISTS idx_ocr_result_fulltext_trgm ON ocr_result USING gin(full_text gin_trgm_ops);

CREATE INDEX IF NOT EXISTS idx_ocr_entity_type_value ON ocr_extracted_entity(entity_type, entity_value);

COMMENT ON TABLE ocr_queue IS 'OCR processing queue - retry-safe, status-tracked';
COMMENT ON TABLE ocr_result IS 'OCR extracted text and confidence scores';
COMMENT ON TABLE ocr_extracted_entity IS 'Named entities extracted from OCR text';

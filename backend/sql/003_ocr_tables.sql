-- ============================================================
-- PLW EDMS — OCR TABLES
-- File: 003_ocr_tables.sql
-- Run order: 3rd (after 001)
-- ============================================================

CREATE TABLE ocr.ocr_queue (
    id SERIAL PRIMARY KEY,
    file_id INTEGER NOT NULL REFERENCES edms.files(id) ON DELETE CASCADE,
    status VARCHAR(50) DEFAULT 'pending',
    priority INTEGER DEFAULT 5,
    attempts INTEGER DEFAULT 0,
    max_attempts INTEGER DEFAULT 3,
    queued_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    last_error TEXT,
    processing_time_seconds INTEGER,
    ocr_engine VARCHAR(50) DEFAULT 'tesseract',
    language VARCHAR(10) DEFAULT 'eng',
    preprocessing_options JSONB,
    worker_id VARCHAR(100),
    assigned_at TIMESTAMP,
    created_by INTEGER REFERENCES public.users(id) ON DELETE SET NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT chk_ocr_status CHECK (
        status IN ('pending','processing','completed','failed','retry','manual_review')
    )
);

CREATE TABLE ocr.ocr_results (
    id SERIAL PRIMARY KEY,
    file_id INTEGER UNIQUE NOT NULL REFERENCES edms.files(id) ON DELETE CASCADE,
    queue_id INTEGER REFERENCES ocr.ocr_queue(id) ON DELETE SET NULL,
    full_text TEXT,
    page_count INTEGER,
    confidence_score NUMERIC(5,2),
    page_results JSONB,
    ocr_engine VARCHAR(50),
    ocr_version VARCHAR(50),
    language_detected VARCHAR(50),
    processing_time_seconds INTEGER,
    file_size_bytes BIGINT,
    processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    indexed_at TIMESTAMP
);

CREATE TABLE ocr.extracted_entities (
    id SERIAL PRIMARY KEY,
    ocr_result_id INTEGER NOT NULL REFERENCES ocr.ocr_results(id) ON DELETE CASCADE,
    entity_type VARCHAR(100) NOT NULL,
    entity_value TEXT NOT NULL,
    confidence NUMERIC(5,2),
    context TEXT,
    page_number INTEGER,
    bounding_box JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes
CREATE INDEX idx_ocr_queue_status   ON ocr.ocr_queue(status);
CREATE INDEX idx_ocr_queue_priority ON ocr.ocr_queue(priority, queued_at);
CREATE INDEX idx_ocr_results_file   ON ocr.ocr_results(file_id);
CREATE INDEX idx_entities_type      ON ocr.extracted_entities(entity_type);
CREATE INDEX idx_entities_value     ON ocr.extracted_entities(entity_value);

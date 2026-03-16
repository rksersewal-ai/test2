-- ============================================================
-- PLW EDMS — AUDIT TABLES
-- File: 002_audit_tables.sql
-- Run order: 2nd (after 001)
-- ============================================================

CREATE TABLE audit.audit_logs (
    id BIGSERIAL PRIMARY KEY,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    user_id INTEGER REFERENCES public.users(id) ON DELETE SET NULL,
    username VARCHAR(150) NOT NULL,
    action VARCHAR(50) NOT NULL,
    module VARCHAR(50) NOT NULL,
    entity_type VARCHAR(100),
    entity_id INTEGER,
    entity_identifier VARCHAR(200),
    description TEXT,
    ip_address INET,
    user_agent TEXT,
    request_method VARCHAR(10),
    request_path TEXT,
    before_value JSONB,
    after_value JSONB,
    changes JSONB,
    success BOOLEAN DEFAULT TRUE,
    error_message TEXT,
    session_id VARCHAR(100)
);

CREATE TABLE audit.document_access_logs (
    id BIGSERIAL PRIMARY KEY,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    user_id INTEGER REFERENCES public.users(id) ON DELETE SET NULL,
    document_id INTEGER,
    revision_id INTEGER,
    file_id INTEGER,
    access_type VARCHAR(50) NOT NULL,
    document_number VARCHAR(100),
    ip_address INET,
    session_id VARCHAR(100)
);

-- Prevent modifications to audit logs via rule
CREATE RULE no_update_audit_logs AS ON UPDATE TO audit.audit_logs DO INSTEAD NOTHING;
CREATE RULE no_delete_audit_logs AS ON DELETE TO audit.audit_logs DO INSTEAD NOTHING;
CREATE RULE no_update_access_logs AS ON UPDATE TO audit.document_access_logs DO INSTEAD NOTHING;
CREATE RULE no_delete_access_logs AS ON DELETE TO audit.document_access_logs DO INSTEAD NOTHING;

-- Indexes
CREATE INDEX idx_audit_timestamp   ON audit.audit_logs(timestamp DESC);
CREATE INDEX idx_audit_user        ON audit.audit_logs(user_id);
CREATE INDEX idx_audit_action      ON audit.audit_logs(action);
CREATE INDEX idx_audit_module      ON audit.audit_logs(module);
CREATE INDEX idx_audit_entity      ON audit.audit_logs(entity_type, entity_id);
CREATE INDEX idx_access_timestamp  ON audit.document_access_logs(timestamp DESC);
CREATE INDEX idx_access_document   ON audit.document_access_logs(document_id);
CREATE INDEX idx_access_user       ON audit.document_access_logs(user_id);

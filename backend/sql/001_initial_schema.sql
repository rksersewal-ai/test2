-- ============================================================
-- PLW EDMS + LDO WORK LEDGER — INITIAL SCHEMA
-- File: 001_initial_schema.sql
-- Version: 1.0
-- Database: PostgreSQL 18+
-- Run order: 1st
-- ============================================================

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";
CREATE EXTENSION IF NOT EXISTS "btree_gin";

CREATE SCHEMA IF NOT EXISTS edms;
CREATE SCHEMA IF NOT EXISTS workflow;
CREATE SCHEMA IF NOT EXISTS audit;
CREATE SCHEMA IF NOT EXISTS ocr;

-- ============================================================
-- PUBLIC SCHEMA — CORE ADMIN
-- ============================================================

CREATE TABLE public.sections (
    id SERIAL PRIMARY KEY,
    code VARCHAR(20) UNIQUE NOT NULL,
    name VARCHAR(200) NOT NULL,
    description TEXT,
    parent_id INTEGER REFERENCES public.sections(id) ON DELETE SET NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by INTEGER,
    updated_by INTEGER
);

CREATE TABLE public.roles (
    id SERIAL PRIMARY KEY,
    code VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    is_system BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE public.users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(150) UNIQUE NOT NULL,
    email VARCHAR(254) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(200) NOT NULL,
    employee_code VARCHAR(50) UNIQUE,
    section_id INTEGER REFERENCES public.sections(id) ON DELETE SET NULL,
    is_active BOOLEAN DEFAULT TRUE,
    is_staff BOOLEAN DEFAULT FALSE,
    is_superuser BOOLEAN DEFAULT FALSE,
    last_login TIMESTAMP,
    password_changed_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE public.user_roles (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
    role_id INTEGER NOT NULL REFERENCES public.roles(id) ON DELETE CASCADE,
    assigned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    assigned_by INTEGER REFERENCES public.users(id) ON DELETE SET NULL,
    UNIQUE(user_id, role_id)
);

CREATE TABLE public.permissions (
    id SERIAL PRIMARY KEY,
    code VARCHAR(100) UNIQUE NOT NULL,
    name VARCHAR(200) NOT NULL,
    module VARCHAR(50) NOT NULL,
    description TEXT,
    is_active BOOLEAN DEFAULT TRUE
);

CREATE TABLE public.role_permissions (
    id SERIAL PRIMARY KEY,
    role_id INTEGER NOT NULL REFERENCES public.roles(id) ON DELETE CASCADE,
    permission_id INTEGER NOT NULL REFERENCES public.permissions(id) ON DELETE CASCADE,
    granted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(role_id, permission_id)
);

-- ============================================================
-- EDMS SCHEMA
-- ============================================================

CREATE TABLE edms.categories (
    id SERIAL PRIMARY KEY,
    code VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(200) NOT NULL,
    description TEXT,
    parent_id INTEGER REFERENCES edms.categories(id) ON DELETE SET NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE edms.document_types (
    id SERIAL PRIMARY KEY,
    code VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(200) NOT NULL,
    description TEXT,
    file_naming_pattern VARCHAR(500),
    retention_years INTEGER,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE edms.documents (
    id SERIAL PRIMARY KEY,
    document_number VARCHAR(100) UNIQUE NOT NULL,
    title VARCHAR(500) NOT NULL,
    description TEXT,
    document_type_id INTEGER REFERENCES edms.document_types(id) ON DELETE SET NULL,
    category_id INTEGER REFERENCES edms.categories(id) ON DELETE SET NULL,
    section_id INTEGER REFERENCES public.sections(id) ON DELETE SET NULL,
    current_revision_id INTEGER,
    status VARCHAR(50) DEFAULT 'draft',
    classification VARCHAR(50) DEFAULT 'internal',
    keywords TEXT[],
    tags TEXT[],
    is_controlled BOOLEAN DEFAULT TRUE,
    is_archived BOOLEAN DEFAULT FALSE,
    created_by INTEGER NOT NULL REFERENCES public.users(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_by INTEGER REFERENCES public.users(id),
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE edms.revisions (
    id SERIAL PRIMARY KEY,
    document_id INTEGER NOT NULL REFERENCES edms.documents(id) ON DELETE CASCADE,
    revision_number VARCHAR(20) NOT NULL,
    revision_date DATE NOT NULL,
    title VARCHAR(500),
    description TEXT,
    change_summary TEXT,
    status VARCHAR(50) DEFAULT 'draft',
    approval_date DATE,
    approval_reference VARCHAR(200),
    effective_date DATE,
    standard_reference VARCHAR(200),
    is_current BOOLEAN DEFAULT FALSE,
    supersedes_revision_id INTEGER REFERENCES edms.revisions(id) ON DELETE SET NULL,
    created_by INTEGER NOT NULL REFERENCES public.users(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_by INTEGER REFERENCES public.users(id),
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(document_id, revision_number)
);

ALTER TABLE edms.documents
    ADD CONSTRAINT fk_current_revision
    FOREIGN KEY (current_revision_id)
    REFERENCES edms.revisions(id) ON DELETE SET NULL;

CREATE TABLE edms.files (
    id SERIAL PRIMARY KEY,
    revision_id INTEGER NOT NULL REFERENCES edms.revisions(id) ON DELETE CASCADE,
    file_name VARCHAR(255) NOT NULL,
    file_path VARCHAR(1000) NOT NULL,
    file_type VARCHAR(50) NOT NULL,
    file_size_bytes BIGINT NOT NULL,
    mime_type VARCHAR(100),
    checksum_sha256 VARCHAR(64),
    page_count INTEGER,
    is_primary BOOLEAN DEFAULT FALSE,
    is_ocr_processed BOOLEAN DEFAULT FALSE,
    ocr_text TEXT,
    ocr_confidence NUMERIC(5,2),
    uploaded_by INTEGER NOT NULL REFERENCES public.users(id),
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    storage_location VARCHAR(50) DEFAULT 'local'
);

CREATE TABLE edms.relationships (
    id SERIAL PRIMARY KEY,
    parent_document_id INTEGER NOT NULL REFERENCES edms.documents(id) ON DELETE CASCADE,
    child_document_id INTEGER NOT NULL REFERENCES edms.documents(id) ON DELETE CASCADE,
    relationship_type VARCHAR(50) NOT NULL,
    description TEXT,
    created_by INTEGER NOT NULL REFERENCES public.users(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(parent_document_id, child_document_id, relationship_type),
    CHECK(parent_document_id != child_document_id)
);

CREATE TABLE edms.metadata (
    id SERIAL PRIMARY KEY,
    document_id INTEGER NOT NULL REFERENCES edms.documents(id) ON DELETE CASCADE,
    key VARCHAR(100) NOT NULL,
    value TEXT,
    value_type VARCHAR(20) DEFAULT 'text',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(document_id, key)
);

-- ============================================================
-- WORKFLOW SCHEMA — LDO WORK LEDGER
-- ============================================================

CREATE TABLE workflow.work_types (
    id SERIAL PRIMARY KEY,
    code VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(300) NOT NULL,
    description TEXT,
    category VARCHAR(100),
    requires_document BOOLEAN DEFAULT FALSE,
    requires_tender BOOLEAN DEFAULT FALSE,
    requires_vendor BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE workflow.vendors (
    id SERIAL PRIMARY KEY,
    vendor_code VARCHAR(50) UNIQUE NOT NULL,
    vendor_name VARCHAR(300) NOT NULL,
    vendor_type VARCHAR(100),
    contact_person VARCHAR(200),
    email VARCHAR(254),
    phone VARCHAR(50),
    address TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE workflow.tenders (
    id SERIAL PRIMARY KEY,
    tender_number VARCHAR(100) UNIQUE NOT NULL,
    tender_title VARCHAR(500) NOT NULL,
    tender_type VARCHAR(100),
    issue_date DATE,
    closing_date DATE,
    opening_date DATE,
    section_id INTEGER REFERENCES public.sections(id) ON DELETE SET NULL,
    status VARCHAR(50) DEFAULT 'draft',
    eoffice_file_number VARCHAR(100),
    description TEXT,
    created_by INTEGER REFERENCES public.users(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE workflow.work_ledger (
    id SERIAL PRIMARY KEY,
    ledger_number VARCHAR(50) UNIQUE NOT NULL,
    work_type_id INTEGER NOT NULL REFERENCES workflow.work_types(id) ON DELETE RESTRICT,
    performed_by INTEGER NOT NULL REFERENCES public.users(id),
    section_id INTEGER REFERENCES public.sections(id) ON DELETE SET NULL,
    received_date DATE NOT NULL,
    started_date DATE,
    completed_date DATE,
    closed_date DATE,
    document_id INTEGER REFERENCES edms.documents(id) ON DELETE SET NULL,
    revision_id INTEGER REFERENCES edms.revisions(id) ON DELETE SET NULL,
    eoffice_file_number VARCHAR(100),
    eoffice_subject TEXT,
    eoffice_reference_date DATE,
    tender_id INTEGER REFERENCES workflow.tenders(id) ON DELETE SET NULL,
    vendor_id INTEGER REFERENCES workflow.vendors(id) ON DELETE SET NULL,
    approval_date DATE,
    approval_authority VARCHAR(200),
    approval_reference VARCHAR(200),
    work_description TEXT NOT NULL,
    remarks TEXT,
    priority VARCHAR(20) DEFAULT 'normal',
    status VARCHAR(50) DEFAULT 'open',
    created_by INTEGER NOT NULL REFERENCES public.users(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_by INTEGER REFERENCES public.users(id),
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT chk_dates_logical CHECK (
        (started_date IS NULL OR started_date >= received_date) AND
        (completed_date IS NULL OR completed_date >= COALESCE(started_date, received_date)) AND
        (closed_date IS NULL OR closed_date >= received_date)
    ),
    CONSTRAINT chk_work_status CHECK (status IN ('open','in_progress','completed','closed','cancelled')),
    CONSTRAINT chk_work_priority CHECK (priority IN ('low','normal','high','urgent'))
);

CREATE TABLE workflow.work_attachments (
    id SERIAL PRIMARY KEY,
    work_ledger_id INTEGER NOT NULL REFERENCES workflow.work_ledger(id) ON DELETE CASCADE,
    file_name VARCHAR(255) NOT NULL,
    file_path VARCHAR(1000) NOT NULL,
    file_type VARCHAR(50),
    file_size_bytes BIGINT,
    description TEXT,
    uploaded_by INTEGER NOT NULL REFERENCES public.users(id),
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================
-- CONSTRAINTS
-- ============================================================

ALTER TABLE edms.documents
    ADD CONSTRAINT chk_document_status
    CHECK (status IN ('draft','under_review','approved','obsolete','archived'));

ALTER TABLE edms.revisions
    ADD CONSTRAINT chk_revision_status
    CHECK (status IN ('draft','under_review','approved','superseded','obsolete'));

ALTER TABLE edms.revisions
    ADD CONSTRAINT chk_revision_dates
    CHECK (
        (approval_date IS NULL OR approval_date >= revision_date) AND
        (effective_date IS NULL OR effective_date >= revision_date)
    );

-- ============================================================
-- INITIAL SEED DATA — ROLES
-- ============================================================

INSERT INTO public.roles (code, name, description, is_system) VALUES
    ('SUPERADMIN',       'Super Administrator',  'Full system access',                        TRUE),
    ('ADMIN',            'Administrator',         'Administrative access to all modules',      TRUE),
    ('LDO_MANAGER',      'LDO Manager',           'Manage LDO work ledger and assignments',    TRUE),
    ('LDO_USER',         'LDO User',              'Create and update work ledger entries',     TRUE),
    ('DOCUMENT_MANAGER', 'Document Manager',      'Manage documents and revisions',            TRUE),
    ('DOCUMENT_VIEWER',  'Document Viewer',       'View documents and search',                 TRUE),
    ('OCR_ADMIN',        'OCR Administrator',     'Manage OCR processing and queue',           TRUE),
    ('AUDIT_VIEWER',     'Audit Viewer',          'View audit logs',                           TRUE);

INSERT INTO public.permissions (code, name, module) VALUES
    ('edms.view_documents',    'View Documents',        'edms'),
    ('edms.create_documents',  'Create Documents',      'edms'),
    ('edms.edit_documents',    'Edit Documents',        'edms'),
    ('edms.delete_documents',  'Delete Documents',      'edms'),
    ('edms.approve_revisions', 'Approve Revisions',     'edms'),
    ('edms.archive_documents', 'Archive Documents',     'edms'),
    ('workflow.view_ledger',   'View Work Ledger',      'workflow'),
    ('workflow.create_ledger', 'Create Work Entries',   'workflow'),
    ('workflow.edit_ledger',   'Edit Work Entries',     'workflow'),
    ('workflow.delete_ledger', 'Delete Work Entries',   'workflow'),
    ('workflow.close_work',    'Close Work Entries',    'workflow'),
    ('workflow.manage_masters','Manage Work Masters',   'workflow'),
    ('ocr.view_queue',         'View OCR Queue',        'ocr'),
    ('ocr.process_ocr',        'Process OCR Jobs',      'ocr'),
    ('ocr.manage_ocr',         'Manage OCR Config',     'ocr'),
    ('admin.manage_users',     'Manage Users',          'admin'),
    ('admin.manage_roles',     'Manage Roles',          'admin'),
    ('admin.manage_sections',  'Manage Sections',       'admin'),
    ('admin.system_config',    'System Configuration',  'admin'),
    ('audit.view_logs',        'View Audit Logs',       'audit'),
    ('audit.export_logs',      'Export Audit Logs',     'audit');

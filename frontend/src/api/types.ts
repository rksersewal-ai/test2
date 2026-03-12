// ─── Auth ─────────────────────────────────────────────────────────────────
export interface TokenResponse {
  access: string;
  refresh: string;
  user_id: number;
  username: string;
  full_name: string;
  role: string;
  section_id: number | null;
  section_name: string | null;
}

// ─── Core ─────────────────────────────────────────────────────────────────
export interface Section {
  id: number;
  code: string;
  name: string;
  description: string;
  parent: number | null;
  parent_name: string | null;
  is_active: boolean;
}

export interface User {
  id: number;
  username: string;
  email: string;
  full_name: string;
  employee_code: string | null;
  designation: string;
  section: number | null;
  section_name: string | null;
  role: string;
  role_display: string;
  is_active: boolean;
  created_at: string;
}

// ─── EDMS ─────────────────────────────────────────────────────────────────
export interface Category {
  id: number;
  code: string;
  name: string;
  description: string;
  parent: number | null;
  is_active: boolean;
}

export interface DocumentType {
  id: number;
  code: string;
  name: string;
  is_active: boolean;
}

export type DocumentStatus = 'ACTIVE' | 'SUPERSEDED' | 'OBSOLETE' | 'DRAFT';

export interface DocumentList {
  id: number;
  document_number: string;
  title: string;
  category: number | null;
  category_name: string | null;
  section: number | null;
  section_name: string | null;
  status: DocumentStatus;
  source_standard: string;
  eoffice_file_number: string;
  revision_count: number;
  created_at: string;
  updated_at: string;
}

export interface FileAttachment {
  id: number;
  revision: number;
  file_name: string;
  file_path: string;
  file_size_bytes: number | null;
  file_type: 'PDF' | 'IMAGE' | 'TIFF';
  page_count: number | null;
  checksum_sha256: string;
  is_primary: boolean;
  uploaded_by: number | null;
  uploaded_at: string;
}

export interface Revision {
  id: number;
  document: number;
  document_number: string;
  revision_number: string;
  revision_date: string | null;
  status: 'CURRENT' | 'SUPERSEDED' | 'DRAFT';
  change_description: string;
  prepared_by: string;
  approved_by: string;
  eoffice_ref: string;
  created_by: number | null;
  created_by_name: string | null;
  created_at: string;
  updated_at: string;
  files: FileAttachment[];
}

export interface DocumentDetail extends DocumentList {
  description: string;
  document_type: number | null;
  eoffice_subject: string;
  keywords: string;
  created_by: number | null;
  created_by_name: string | null;
  revisions: Revision[];
}

// ─── Workflow ─────────────────────────────────────────────────────────────
export type WorkLedgerStatus = 'OPEN' | 'IN_PROGRESS' | 'CLOSED' | 'ON_HOLD';

export interface WorkLedger {
  id: number;
  work_type: number | null;
  work_type_name: string | null;
  section: number | null;
  section_name: string | null;
  assigned_to: number | null;
  assigned_to_name: string | null;
  status: WorkLedgerStatus;
  received_date: string | null;
  target_date: string | null;
  closed_date: string | null;
  eoffice_file_number: string;
  eoffice_subject: string;
  document: number | null;
  document_number: string | null;
  revision: number | null;
  tender: number | null;
  tender_number: string | null;
  vendor: number | null;
  vendor_name: string | null;
  subject: string;
  remarks: string;
  created_by: number | null;
  created_by_name: string | null;
  created_at: string;
  updated_at: string;
}

export interface Tender {
  id: number;
  tender_number: string;
  title: string;
  description: string;
  status: 'OPEN' | 'EVALUATION' | 'CLOSED' | 'CANCELLED';
  issue_date: string | null;
  closing_date: string | null;
  eoffice_file_number: string;
  created_by: number | null;
  created_by_name: string | null;
  created_at: string;
}

// ─── OCR ──────────────────────────────────────────────────────────────────
export type OCRStatus = 'PENDING' | 'PROCESSING' | 'COMPLETED' | 'FAILED' | 'RETRY' | 'MANUAL_REVIEW';

export interface OCRQueue {
  id: number;
  file: number;
  file_name: string;
  status: OCRStatus;
  priority: number;
  attempts: number;
  max_attempts: number;
  queued_at: string;
  started_at: string | null;
  completed_at: string | null;
  last_error: string;
  processing_time_seconds: number | null;
  ocr_engine: string;
  language: string;
  created_by: number | null;
  created_by_name: string | null;
  created_at: string;
}

export interface OCRResult {
  id: number;
  file: number;
  file_name: string;
  full_text: string;
  page_count: number | null;
  confidence_score: number | null;
  page_results: { page: number; text: string }[];
  ocr_engine: string;
  language_detected: string;
  processing_time_seconds: number | null;
  processed_at: string;
  entities: ExtractedEntity[];
}

export interface ExtractedEntity {
  id: number;
  entity_type: string;
  entity_value: string;
  confidence: number | null;
  context: string;
  page_number: number | null;
}

// ─── Audit ────────────────────────────────────────────────────────────────
export interface AuditLog {
  id: number;
  timestamp: string;
  user: number | null;
  username: string;
  user_full_name: string | null;
  action: string;
  module: string;
  entity_type: string;
  entity_id: string;
  entity_identifier: string;
  description: string;
  ip_address: string | null;
  success: boolean;
  error_message: string;
}

// ─── Dashboard ────────────────────────────────────────────────────────────
export interface DashboardStats {
  documents: { total: number; active: number; draft: number };
  work_ledger: { total: number; open: number; in_progress: number; closed: number; closed_last_30: number };
  ocr_queue: { pending: number; processing: number; completed: number; failed: number; manual_review: number };
  documents_by_section: { section__name: string | null; count: number }[];
  generated_at: string;
}

// ─── Pagination ───────────────────────────────────────────────────────────
export interface PaginatedResponse<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}

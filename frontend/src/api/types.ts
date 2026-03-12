/** Central TypeScript types for all EDMS API contracts */

export interface PaginatedResponse<T> {
  count:    number;
  next:     string | null;
  previous: string | null;
  results:  T[];
}

export type DocumentStatus = 'ACTIVE' | 'DRAFT' | 'OBSOLETE' | 'SUPERSEDED';
export type RevisionStatus = 'CURRENT' | 'SUPERSEDED' | 'DRAFT';
export type WorkLedgerStatus = 'OPEN' | 'IN_PROGRESS' | 'ON_HOLD' | 'CLOSED';
export type OCRStatus = 'PENDING' | 'PROCESSING' | 'COMPLETED' | 'FAILED' | 'RETRY' | 'MANUAL_REVIEW';

export interface TokenResponse { access: string; refresh: string; }

export interface User {
  id:        number;
  username:  string;
  full_name: string;
  role:      string;
  section?:  string;
}

export interface FileAttachment {
  id:            number;
  file_name:     string;
  file_url:      string;
  file_size:     number;
  file_type:     string;
  uploaded_at:   string;
  ocr_status?:   OCRStatus;
}

export interface Revision {
  id:                 number;
  revision_number:    string;
  revision_date:      string | null;
  status:             RevisionStatus;
  change_description: string;
  eoffice_ref:        string;
  files:              FileAttachment[];
}

export interface DocumentList {
  id:              number;
  document_number: string;
  title:           string;
  status:          DocumentStatus;
  category_name:   string | null;
  section_name:    string | null;
  source_standard: string;
  revision_count:  number;
  updated_at:      string;
}

export interface DocumentDetail extends DocumentList {
  description:          string;
  keywords:             string;
  eoffice_file_number:  string;
  eoffice_subject:      string;
  created_at:           string;
  created_by_name:      string;
  revisions:            Revision[];
}

export interface WorkLedger {
  id:                 number;
  subject:            string;
  eoffice_subject:    string;
  eoffice_file_number: string;
  work_type_name:     string | null;
  section_name:       string | null;
  assigned_to_name:   string | null;
  status:             WorkLedgerStatus;
  target_date:        string | null;
  created_at:         string;
}

export interface OCRQueue {
  id:                      number;
  file_name:               string;
  status:                  OCRStatus;
  priority:                number;
  attempts:                number;
  max_attempts:            number;
  ocr_engine:              string;
  queued_at:               string;
  completed_at:            string | null;
  processing_time_seconds: number | null;
  error_message?:          string;
}

export interface AuditLog {
  id:             number;
  timestamp:      string;
  username:       string;
  user_full_name: string;
  module:         string;
  action:         string;
  entity_type:    string;
  entity_identifier: string;
  description:    string;
  ip_address:     string | null;
  success:        boolean;
}

export interface DashboardStats {
  generated_at:  string;
  documents: { total: number; active: number; draft: number; obsolete: number; };
  work_ledger: { open: number; in_progress: number; on_hold: number; closed: number; };
  ocr_queue:  { pending: number; processing: number; completed: number; failed: number; };
  documents_by_section: { section__name: string | null; count: number; }[];
}

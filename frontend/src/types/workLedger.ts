// =============================================================================
// FILE: frontend/src/types/workLedger.ts
// PURPOSE: Shared TypeScript types for Work Ledger module
// =============================================================================

export type WorkSection = 'Mechanical' | 'Electrical' | 'General';
export type WorkStatus = 'Open' | 'Closed' | 'Pending';

export interface WorkCategory {
  code: string;
  label: string;
  sort_order: number;
}

export interface WorkLedgerDetail {
  field_name: string;
  field_value: string | null;
}

export interface WorkLedgerAttachment {
  attachment_id: number;
  document_id: number | null;
  file_name: string;
  mime_type: string | null;
  file_size_kb: number | null;
  uploaded_at: string;
}

export interface WorkLedgerListItem {
  work_id: number;
  work_code: string;
  received_date: string;
  closed_date: string | null;
  section: WorkSection;
  status: WorkStatus;
  pl_number: string | null;
  drawing_number: string | null;
  tender_number: string | null;
  work_category_code: string;
  work_category_label: string;
  description: string;
  remarks: string | null;
  created_at: string;
}

export interface WorkLedgerFull extends WorkLedgerListItem {
  engineer_id: number;
  officer_id: number | null;
  drawing_revision: string | null;
  specification_number: string | null;
  specification_revision: string | null;
  case_number: string | null;
  eoffice_file_no: string | null;
  details: WorkLedgerDetail[];
  attachments: WorkLedgerAttachment[];
}

export interface WorkLedgerFormData {
  received_date: string;
  closed_date: string;
  section: WorkSection;
  engineer_id: number | null;
  officer_id: number | null;
  status: WorkStatus;
  pl_number: string;
  drawing_number: string;
  drawing_revision: string;
  specification_number: string;
  specification_revision: string;
  tender_number: string;
  case_number: string;
  eoffice_file_no: string;
  work_category_code: string;
  description: string;
  remarks: string;
  details: WorkLedgerDetail[];
}

export interface ActivityReportRow {
  work_id: number;
  work_code: string;
  received_date: string;
  closed_date: string | null;
  section: WorkSection;
  engineer_id: number;
  officer_id: number | null;
  work_category_label: string;
  pl_number: string | null;
  drawing_number: string | null;
  tender_number: string | null;
  status: WorkStatus;
  remarks: string | null;
}

export interface KpiRow {
  work_category_code: string;
  work_category_label: string;
  work_count: number;
}

export interface MonthlyKpiResponse {
  month: string;
  summary: KpiRow[];
}

export interface DashboardSummary {
  month: string;
  total: number;
  by_category: KpiRow[];
}

export interface ActivityReportFilters {
  from_date?: string;
  to_date?: string;
  section?: string;
  engineer_id?: number;
  officer_id?: number;
  category?: string;
  pl_number?: string;
  status?: string;
}

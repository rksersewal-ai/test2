// =============================================================================
// FILE: frontend/src/services/workLedgerService.ts
// BUG FIX: WorkLedgerPage called methods that did not exist in this service.
// Added: listEntries, getEntry, createEntry, updateEntry, deleteEntry,
//        submitEntry, verifyEntry, listCategories, downloadReport
// Also fixed baseURL prefix: /work-ledger/ (matches config/urls.py → work/)
// NOTE: backend mounts at /api/v1/work/ — Vite proxy handles /api/v1 prefix.
// =============================================================================
import apiClient from './apiClient';
import type { PaginatedResponse } from '../api/types';

export interface WorkLedgerEntry {
  id               : number;
  work_date        : string;
  work_description : string;
  category         : number | null;
  category_name    : string;
  work_type        : string;
  hours_spent      : number | string;
  reference_number : string;
  eoffice_file_no  : string;
  remarks          : string;
  status           : 'DRAFT' | 'SUBMITTED' | 'VERIFIED' | 'APPROVED' | 'RETURNED';
  created_by       : string;
  verified_by      : string | null;
  verified_at      : string | null;
  verifier_remarks : string;
  created_at       : string;
  updated_at       : string;
}

export interface WorkCategory {
  id            : number;
  category_name : string;
  description   : string;
  is_active     : boolean;
}

export interface WorkLedgerFilters {
  page?      : number;
  page_size? : number;
  status?    : string;
  work_type? : string;
  search?    : string;
}

// Backend is mounted at /api/v1/work/ in config/urls.py
const BASE = '/work';

export const workLedgerService = {

  // ── Entries ────────────────────────────────────────────────────────────────

  /** List work entries with optional filters/search/pagination */
  listEntries: (params: Record<string, string | number> = {}) =>
    apiClient
      .get<PaginatedResponse<WorkLedgerEntry>>(`${BASE}/entries/`, { params })
      .then(r => r.data),

  /** Get a single entry by ID */
  getEntry: (id: number) =>
    apiClient
      .get<WorkLedgerEntry>(`${BASE}/entries/${id}/`)
      .then(r => r.data),

  /** Create a new DRAFT entry */
  createEntry: (data: Partial<WorkLedgerEntry>) =>
    apiClient
      .post<WorkLedgerEntry>(`${BASE}/entries/`, data)
      .then(r => r.data),

  /** Partial-update an existing entry */
  updateEntry: (id: number, data: Partial<WorkLedgerEntry>) =>
    apiClient
      .patch<WorkLedgerEntry>(`${BASE}/entries/${id}/`, data)
      .then(r => r.data),

  /** Delete a DRAFT entry */
  deleteEntry: (id: number) =>
    apiClient.delete(`${BASE}/entries/${id}/`),

  /** Submit a DRAFT entry for verification */
  submitEntry: (id: number) =>
    apiClient
      .post<WorkLedgerEntry>(`${BASE}/entries/${id}/submit/`)
      .then(r => r.data),

  /** Verify or return a SUBMITTED entry.
   *  action = 'VERIFY' | 'RETURN'
   */
  verifyEntry: (id: number, action: 'VERIFY' | 'RETURN', remarks = '') =>
    apiClient
      .post<WorkLedgerEntry>(`${BASE}/entries/${id}/verify/`, { action, remarks })
      .then(r => r.data),

  // ── Categories ─────────────────────────────────────────────────────────────

  /** Fetch all active work categories (used in the form dropdown) */
  listCategories: (params: Record<string, string> = {}) =>
    apiClient
      .get<PaginatedResponse<WorkCategory> | WorkCategory[]>(`${BASE}/categories/`, { params })
      .then(r => r.data),

  // ── Reports ────────────────────────────────────────────────────────────────

  /**
   * Download monthly report as PDF or Excel.
   * format = 'pdf' → GET /work/report/?year=…&month=…
   * format = 'excel' → GET /work/report/excel/?year=…&month=…
   */
  downloadReport: (year: number, month: number, format: 'pdf' | 'excel'): Promise<Blob> => {
    const url = format === 'excel' ? `${BASE}/report/excel/` : `${BASE}/report/`;
    return apiClient
      .get(url, { params: { year, month }, responseType: 'blob' })
      .then(r => r.data as Blob);
  },

  // ── Dashboard / summary ────────────────────────────────────────────────────

  /** My-entries summary (counts by status) */
  myEntries: () =>
    apiClient
      .get(`${BASE}/entries/my-entries/`)
      .then(r => r.data),

  /** Team summary (supervisors / staff only) */
  teamSummary: () =>
    apiClient
      .get(`${BASE}/entries/team-summary/`)
      .then(r => r.data),

  // ── Legacy aliases (kept so workLedger.ts / workLedgerApi.ts re-exports
  //    don't break any other file that still uses the old names) ────────────

  list   : (params: Record<string, string | number> = {}) =>
    apiClient
      .get<PaginatedResponse<WorkLedgerEntry>>(`${BASE}/entries/`, { params })
      .then(r => r.data),

  get    : (id: number) =>
    apiClient.get<WorkLedgerEntry>(`${BASE}/entries/${id}/`).then(r => r.data),

  create : (data: Partial<WorkLedgerEntry>) =>
    apiClient.post<WorkLedgerEntry>(`${BASE}/entries/`, data).then(r => r.data),

  update : (id: number, data: Partial<WorkLedgerEntry>) =>
    apiClient.patch<WorkLedgerEntry>(`${BASE}/entries/${id}/`, data).then(r => r.data),

  remove : (id: number) =>
    apiClient.delete(`${BASE}/entries/${id}/`),

  dashboard: () =>
    apiClient.get(`${BASE}/entries/my-entries/`).then(r => r.data),

  report: (params: Record<string, string> = {}) =>
    apiClient.get(`${BASE}/report/`, { params }).then(r => r.data),

  exportCsv: (params: Record<string, string> = {}): Promise<Blob> =>
    apiClient
      .get(`${BASE}/report/excel/`, { params, responseType: 'blob' })
      .then(r => r.data as Blob),
};

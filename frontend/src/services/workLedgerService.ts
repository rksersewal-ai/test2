// =============================================================================
// FILE: frontend/src/services/workLedgerService.ts
// ADDED: getMonthlyKpi, getActivityReport, getExportUrl, getCategories
//   — required by MonthlyKpiReportPage and WorkActivityReportPage but
//     were missing, causing runtime TypeError on those pages.
// Base URL corrected: /work-ledger/ (matches config/urls.py after Fix 3)
// =============================================================================
import api from '../api/axios';
import type { PaginatedResponse } from '../api/types';
import type {
  WorkLedgerListItem,
  WorkLedgerFull,
  WorkLedgerFormData,
  ActivityReportFilters,
  ActivityReportRow,
  MonthlyKpiResponse,
  WorkCategory,
} from '../types/workLedger';

const BASE = '/work-ledger';

export const workLedgerService = {
  // ── Entries ────────────────────────────────────────────────────────────────
  listEntries: (params?: Record<string, string>) =>
    api.get<PaginatedResponse<WorkLedgerListItem>>(`${BASE}/entries/`, { params }).then(r => r.data),

  getEntry: (id: number) =>
    api.get<WorkLedgerFull>(`${BASE}/entries/${id}/`).then(r => r.data),

  createEntry: (data: Partial<WorkLedgerFormData>) =>
    api.post<WorkLedgerFull>(`${BASE}/entries/`, data).then(r => r.data),

  updateEntry: (id: number, data: Partial<WorkLedgerFormData>) =>
    api.patch<WorkLedgerFull>(`${BASE}/entries/${id}/`, data).then(r => r.data),

  deleteEntry: (id: number) =>
    api.delete(`${BASE}/entries/${id}/`).then(r => r.data),

  submitEntry: (id: number) =>
    api.post(`${BASE}/entries/${id}/submit/`).then(r => r.data),

  verifyEntry: (id: number, action: 'approve' | 'reject', remarks?: string) =>
    api.post(`${BASE}/entries/${id}/verify/`, { action, remarks }).then(r => r.data),

  // ── Categories ─────────────────────────────────────────────────────────────
  /**
   * BUG FIX: WorkActivityReportPage called getCategories() — was missing.
   * GET /work-ledger/categories/
   */
  listCategories: () =>
    api.get<WorkCategory[]>(`${BASE}/categories/`).then(r => r.data),

  getCategories: () =>
    api.get<WorkCategory[]>(`${BASE}/categories/`).then(r => r.data),

  // ── Reports ────────────────────────────────────────────────────────────────
  /**
   * BUG FIX: MonthlyKpiReportPage called getMonthlyKpi(year, month, section)
   * — method was missing entirely.
   * GET /work-ledger/report/kpi/?year=&month=&section=
   */
  getMonthlyKpi: (year: number, month: number, section?: string) => {
    const params: Record<string, string> = {
      year:  String(year),
      month: String(month),
    };
    if (section) params.section = section;
    return api.get<MonthlyKpiResponse>(`${BASE}/report/kpi/`, { params }).then(r => r.data);
  },

  /**
   * BUG FIX: WorkActivityReportPage called getActivityReport(filters)
   * — method was missing entirely.
   * GET /work-ledger/report/activity/
   */
  getActivityReport: (filters: ActivityReportFilters) => {
    const params: Record<string, string> = {};
    if (filters.from_date)   params.from_date    = filters.from_date;
    if (filters.to_date)     params.to_date      = filters.to_date;
    if (filters.section)     params.section      = filters.section;
    if (filters.engineer_id) params.engineer_id  = String(filters.engineer_id);
    if (filters.officer_id)  params.officer_id   = String(filters.officer_id);
    if (filters.category)    params.category     = filters.category;
    if (filters.pl_number)   params.pl_number    = filters.pl_number;
    if (filters.status)      params.status       = filters.status;
    return api.get<ActivityReportRow[]>(`${BASE}/report/activity/`, { params }).then(r => r.data);
  },

  /**
   * BUG FIX: WorkActivityReportPage called getExportUrl(filters, fmt)
   * — method was missing. Returns a direct download URL (opened via window.open).
   * GET /work-ledger/report/export/?format=csv|xlsx|pdf&...
   */
  getExportUrl: (filters: ActivityReportFilters, fmt: 'csv' | 'xlsx' | 'pdf'): string => {
    const params = new URLSearchParams({ format: fmt });
    if (filters.from_date)   params.set('from_date',   filters.from_date);
    if (filters.to_date)     params.set('to_date',     filters.to_date);
    if (filters.section)     params.set('section',     filters.section);
    if (filters.engineer_id) params.set('engineer_id', String(filters.engineer_id));
    if (filters.officer_id)  params.set('officer_id',  String(filters.officer_id));
    if (filters.category)    params.set('category',    filters.category);
    if (filters.pl_number)   params.set('pl_number',   filters.pl_number);
    if (filters.status)      params.set('status',      filters.status);
    // Use relative path — will be prefixed by axios baseURL in practice
    return `${BASE}/report/export/?${params.toString()}`;
  },

  downloadReport: (year: number, month: number, format: 'pdf' | 'xlsx' = 'xlsx') =>
    api.get(`${BASE}/report/`, {
      params: { year, month, format },
      responseType: 'blob',
    }).then(r => r.data),

  // ── Legacy aliases (keep for backward compat) ──────────────────────────────
  list:      (p?: Record<string, string>) => workLedgerService.listEntries(p),
  get:       (id: number)                 => workLedgerService.getEntry(id),
  create:    (d: Partial<WorkLedgerFormData>) => workLedgerService.createEntry(d),
  update:    (id: number, d: Partial<WorkLedgerFormData>) => workLedgerService.updateEntry(id, d),
  remove:    (id: number)                 => workLedgerService.deleteEntry(id),
  dashboard: ()                           => workLedgerService.getMonthlyKpi(new Date().getFullYear(), new Date().getMonth() + 1),
  report:    (y: number, m: number)       => workLedgerService.getMonthlyKpi(y, m),
  exportCsv: (f: ActivityReportFilters)   => workLedgerService.getExportUrl(f, 'csv'),
};

// =============================================================================
// FILE: frontend/src/services/workLedgerApi.ts
// FIX (#8): Replaced localStorage token injection with cookie-based apiFetch.
// FIX (#6): API now returns paginated envelopes - updated response types.
// =============================================================================
import { apiFetch } from './authApi';
import type { WorkLedgerFormData, WorkLedgerListItem, WorkLedgerDetail } from '../types/workLedger';

const BASE = '/api/work-ledger';

export interface PaginatedResponse<T> {
  results:     T[];
  total_count: number;
  page:        number;
  page_size:   number;
  total_pages: number;
}

export const workLedgerApi = {
  list(params?: {
    section?: string;
    status?: string;
    engineer_id?: number;
    page?: number;
    page_size?: number;
  }): Promise<PaginatedResponse<WorkLedgerListItem>> {
    const qs = new URLSearchParams(
      Object.entries(params ?? {}).filter(([, v]) => v != null).map(([k, v]) => [k, String(v)])
    ).toString();
    return apiFetch(`${BASE}/entries/?${qs}`);
  },

  get(workId: string): Promise<WorkLedgerDetail> {
    return apiFetch(`${BASE}/entries/${workId}/`);
  },

  create(data: WorkLedgerFormData): Promise<WorkLedgerDetail> {
    return apiFetch(`${BASE}/entries/`, {
      method: 'POST',
      body: JSON.stringify(data),
    });
  },

  update(workId: string, data: WorkLedgerFormData): Promise<WorkLedgerDetail> {
    return apiFetch(`${BASE}/entries/${workId}/`, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  },

  activityReport(params?: Record<string, string>): Promise<PaginatedResponse<any>> {
    const qs = new URLSearchParams(params ?? {}).toString();
    return apiFetch(`${BASE}/reports/activity/?${qs}`);
  },

  monthlyKpi(year: number, month: number, section?: string): Promise<any> {
    const qs = new URLSearchParams(
      Object.entries({ year, month, ...(section ? { section } : {}) }).map(([k, v]) => [k, String(v)])
    ).toString();
    return apiFetch(`${BASE}/reports/monthly-kpi/?${qs}`);
  },

  dashboardSummary(year: number, month: number): Promise<any> {
    return apiFetch(`${BASE}/dashboard/monthly-summary/?year=${year}&month=${month}`);
  },

  exportUrl(params?: Record<string, string>): string {
    const qs = new URLSearchParams({ format: 'csv', ...(params ?? {}) }).toString();
    return `${BASE}/reports/activity/export/?${qs}`;
  },
};

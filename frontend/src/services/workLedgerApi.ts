// =============================================================================
// FILE: frontend/src/services/workLedgerApi.ts
// PURPOSE: API client for Work Ledger endpoints
// =============================================================================
import type {
  WorkCategory,
  WorkLedgerListItem,
  WorkLedgerFull,
  WorkLedgerFormData,
  ActivityReportRow,
  MonthlyKpiResponse,
  DashboardSummary,
  ActivityReportFilters,
} from '../types/workLedger';

const BASE = '/api/work-ledger';

async function apiFetch<T>(url: string, options?: RequestInit): Promise<T> {
  const token = localStorage.getItem('access_token');
  const res = await fetch(url, {
    headers: {
      'Content-Type': 'application/json',
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
    },
    ...options,
  });
  if (!res.ok) throw new Error(`API error ${res.status}: ${await res.text()}`);
  return res.json();
}

export const workLedgerApi = {
  getCategories(): Promise<WorkCategory[]> {
    return apiFetch(`${BASE}/categories/`);
  },

  listEntries(params?: Record<string, string>): Promise<WorkLedgerListItem[]> {
    const qs = params ? '?' + new URLSearchParams(params).toString() : '';
    return apiFetch(`${BASE}/entries/${qs}`);
  },

  getEntry(workId: number): Promise<WorkLedgerFull> {
    return apiFetch(`${BASE}/entries/${workId}/`);
  },

  createEntry(data: WorkLedgerFormData): Promise<WorkLedgerFull> {
    return apiFetch(`${BASE}/entries/`, {
      method: 'POST',
      body: JSON.stringify(data),
    });
  },

  updateEntry(workId: number, data: Partial<WorkLedgerFormData>): Promise<WorkLedgerFull> {
    return apiFetch(`${BASE}/entries/${workId}/`, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  },

  getDashboard(year?: number, month?: number): Promise<DashboardSummary> {
    const qs = year && month ? `?year=${year}&month=${month}` : '';
    return apiFetch(`${BASE}/dashboard/monthly-summary/${qs}`);
  },

  getActivityReport(filters: ActivityReportFilters): Promise<ActivityReportRow[]> {
    const qs = '?' + new URLSearchParams(filters as Record<string, string>).toString();
    return apiFetch(`${BASE}/reports/activity/${qs}`);
  },

  getMonthlyKpi(year: number, month: number, section?: string): Promise<MonthlyKpiResponse> {
    let qs = `?year=${year}&month=${month}`;
    if (section) qs += `&section=${section}`;
    return apiFetch(`${BASE}/reports/monthly-kpi/${qs}`);
  },

  getExportUrl(filters: ActivityReportFilters, format: 'csv' | 'xlsx' | 'pdf'): string {
    const params = { ...filters, format } as Record<string, string>;
    return `${BASE}/reports/activity/export/?` + new URLSearchParams(params).toString();
  },
};

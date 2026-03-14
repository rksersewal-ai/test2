// =============================================================================
// FILE: frontend/src/services/workLedgerService.ts
// CANONICAL work ledger service. workLedger.ts and workLedgerApi.ts both
// re-export from here. Uses shared apiClient (withCredentials set globally).
// =============================================================================
import apiClient from './apiClient';
import type { PaginatedResponse } from '../api/types';

export interface WorkLedgerEntry {
  id          : number;
  work_code   : string;
  loco_no     : string;
  work_date   : string;
  category    : string;
  description : string;
  status      : 'pending' | 'in_progress' | 'completed' | 'cancelled';
  created_by  : string;
  created_at  : string;
  updated_at  : string;
}

export interface WorkLedgerFilters {
  page?     : number;
  page_size?: number;
  status?   : string;
  category? : string;
  loco_no?  : string;
  from_date?: string;
  to_date?  : string;
  search?   : string;
}

export const workLedgerService = {
  async list(filters: WorkLedgerFilters = {}) {
    const { data } = await apiClient.get<PaginatedResponse<WorkLedgerEntry>>(
      '/work-ledger/entries/', { params: filters }
    );
    return data;
  },

  async get(id: number) {
    const { data } = await apiClient.get<WorkLedgerEntry>(`/work-ledger/entries/${id}/`);
    return data;
  },

  async create(payload: Partial<WorkLedgerEntry>) {
    const { data } = await apiClient.post<WorkLedgerEntry>('/work-ledger/entries/', payload);
    return data;
  },

  async update(id: number, payload: Partial<WorkLedgerEntry>) {
    const { data } = await apiClient.patch<WorkLedgerEntry>(`/work-ledger/entries/${id}/`, payload);
    return data;
  },

  async remove(id: number) {
    await apiClient.delete(`/work-ledger/entries/${id}/`);
  },

  async dashboard() {
    const { data } = await apiClient.get('/work-ledger/dashboard/');
    return data;
  },

  async report(params: Record<string, string> = {}) {
    const { data } = await apiClient.get('/work-ledger/report/', { params });
    return data;
  },

  async exportCsv(params: Record<string, string> = {}): Promise<Blob> {
    const { data } = await apiClient.get('/work-ledger/export/', {
      params,
      responseType: 'blob',
    });
    return data;
  },
};

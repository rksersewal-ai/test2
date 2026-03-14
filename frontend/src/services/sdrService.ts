// =============================================================================
// FILE: frontend/src/services/sdrService.ts
// =============================================================================
import api from '../api/axios';
import type { SDRRecord, SDRRecordForm, DocSearchResult } from '../types/sdr';

const BASE = '/sdr';

export const sdrService = {
  list: (params?: Record<string, string>) =>
    api.get<SDRRecord[]>(BASE + '/', { params }).then(r => r.data),

  get: (id: number) =>
    api.get<SDRRecord>(`${BASE}/${id}/`).then(r => r.data),

  create: (data: SDRRecordForm) =>
    api.post<SDRRecord>(BASE + '/', data).then(r => r.data),

  update: (id: number, data: SDRRecordForm) =>
    api.put<SDRRecord>(`${BASE}/${id}/`, data).then(r => r.data),

  delete: (id: number) =>
    api.delete(`${BASE}/${id}/`),

  search: (q: string, type?: 'DRAWING' | 'SPEC') =>
    api.get<DocSearchResult[]>(`${BASE}/search/`, {
      params: type ? { q, type } : { q },
    }).then(r => r.data),
};

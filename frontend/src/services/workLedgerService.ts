// =============================================================================
// FILE: frontend/src/services/workLedgerService.ts
// =============================================================================
import api from '../api/axios';

const BASE = '/work';

export const workLedgerService = {
  listEntries: (params?: Record<string, string>) =>
    api.get(`${BASE}/entries/`, { params }).then(r => r.data),
  getEntry: (id: number) =>
    api.get(`${BASE}/entries/${id}/`).then(r => r.data),
  createEntry: (data: any) =>
    api.post(`${BASE}/entries/`, data).then(r => r.data),
  updateEntry: (id: number, data: any) =>
    api.patch(`${BASE}/entries/${id}/`, data).then(r => r.data),
  deleteEntry: (id: number) =>
    api.delete(`${BASE}/entries/${id}/`),
  submitEntry: (id: number) =>
    api.post(`${BASE}/entries/${id}/submit/`).then(r => r.data),
  verifyEntry: (id: number, action: 'VERIFY' | 'RETURN', remarks?: string) =>
    api.post(`${BASE}/entries/${id}/verify/`, { action, remarks }).then(r => r.data),
  myEntries: () =>
    api.get(`${BASE}/entries/my-entries/`).then(r => r.data),
  teamSummary: () =>
    api.get(`${BASE}/entries/team-summary/`).then(r => r.data),
  listCategories: () =>
    api.get(`${BASE}/categories/`).then(r => r.data),
  downloadReport: (year: number, month: number, format: 'pdf' | 'excel') =>
    api.get(`${BASE}/report/${format === 'excel' ? 'excel/' : ''}`, {
      params: { year, month },
      responseType: 'blob',
    }).then(r => r.data),
};

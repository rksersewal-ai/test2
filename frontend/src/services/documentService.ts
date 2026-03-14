// =============================================================================
// FILE: frontend/src/services/documentService.ts
// =============================================================================
import api from '../api/axios';

const BASE = '/edms';

export const documentService = {
  list: (params?: Record<string, string>) =>
    api.get(`${BASE}/documents/`, { params }).then(r => r.data),
  get: (id: number) =>
    api.get(`${BASE}/documents/${id}/`).then(r => r.data),
  create: (formData: FormData) =>
    api.post(`${BASE}/documents/`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    }).then(r => r.data),
  update: (id: number, data: any) =>
    api.patch(`${BASE}/documents/${id}/`, data).then(r => r.data),
  delete: (id: number) =>
    api.delete(`${BASE}/documents/${id}/`),
  approve: (id: number) =>
    api.post(`${BASE}/documents/${id}/approve/`).then(r => r.data),
  reject: (id: number, reason: string) =>
    api.post(`${BASE}/documents/${id}/reject/`, { reason }).then(r => r.data),
  supersede: (id: number, newId: number) =>
    api.post(`${BASE}/documents/${id}/supersede/`, { new_document: newId }).then(r => r.data),
  downloadFile: (id: number) =>
    api.get(`${BASE}/documents/${id}/download/`, { responseType: 'blob' }).then(r => r.data),
  listVersions: (id: number) =>
    api.get(`${BASE}/documents/${id}/versions/`).then(r => r.data),
  listCategories: () =>
    api.get(`${BASE}/categories/`).then(r => r.data),
  listCorrespondents: () =>
    api.get(`${BASE}/correspondents/`).then(r => r.data),
  listTags: () =>
    api.get(`${BASE}/tags/`).then(r => r.data),
  dashboardStats: () =>
    api.get(`${BASE}/dashboard/`).then(r => r.data),
};

// =============================================================================
// FILE: frontend/src/services/prototypeService.ts
// =============================================================================
import api from '../api/axios';

const BASE = '/prototype';

export const prototypeService = {
  listInspections: (params?: Record<string, string>) =>
    api.get(`${BASE}/inspections/`, { params }).then(r => r.data),
  getInspection: (id: number) =>
    api.get(`${BASE}/inspections/${id}/`).then(r => r.data),
  createInspection: (data: any) =>
    api.post(`${BASE}/inspections/`, data).then(r => r.data),
  updateInspection: (id: number, data: any) =>
    api.patch(`${BASE}/inspections/${id}/`, data).then(r => r.data),
  closeInspection: (id: number) =>
    api.post(`${BASE}/inspections/${id}/close/`).then(r => r.data),

  listPunchItems: (inspectionId: number) =>
    api.get(`${BASE}/inspections/${inspectionId}/punch-items/`).then(r => r.data),
  createPunchItem: (inspectionId: number, data: any) =>
    api.post(`${BASE}/inspections/${inspectionId}/punch-items/`, data).then(r => r.data),
  closePunchItem: (inspectionId: number, punchId: number) =>
    api.post(`${BASE}/inspections/${inspectionId}/punch-items/${punchId}/close/`).then(r => r.data),
};

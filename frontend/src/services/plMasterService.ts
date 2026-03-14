// =============================================================================
// FILE: frontend/src/services/plMasterService.ts
// =============================================================================
import api from '../api/axios';

const BASE = '/pl-master';

export const plMasterService = {
  // PL Master
  listPL: (params?: Record<string, string>) =>
    api.get(`${BASE}/`, { params }).then(r => r.data),
  getPL: (plNumber: string) =>
    api.get(`${BASE}/${plNumber}/`).then(r => r.data),
  createPL: (data: any) =>
    api.post(`${BASE}/`, data).then(r => r.data),
  updatePL: (plNumber: string, data: any) =>
    api.patch(`${BASE}/${plNumber}/`, data).then(r => r.data),
  deletePL: (plNumber: string) =>
    api.delete(`${BASE}/${plNumber}/`),
  getBOMTree: (plNumber: string, maxDepth = 5) =>
    api.get(`${BASE}/${plNumber}/bom/`, { params: { max_depth: maxDepth } }).then(r => r.data),

  // Drawings
  listDrawings: (params?: Record<string, string>) =>
    api.get(`${BASE}/drawings/`, { params }).then(r => r.data),
  getDrawing: (drawingNumber: string) =>
    api.get(`${BASE}/drawings/${drawingNumber}/`).then(r => r.data),
  createDrawing: (data: any) =>
    api.post(`${BASE}/drawings/`, data).then(r => r.data),
  updateDrawing: (drawingNumber: string, data: any) =>
    api.patch(`${BASE}/drawings/${drawingNumber}/`, data).then(r => r.data),

  // Specifications
  listSpecs: (params?: Record<string, string>) =>
    api.get(`${BASE}/specifications/`, { params }).then(r => r.data),
  getSpec: (specNumber: string) =>
    api.get(`${BASE}/specifications/${specNumber}/`).then(r => r.data),
  createSpec: (data: any) =>
    api.post(`${BASE}/specifications/`, data).then(r => r.data),
  updateSpec: (specNumber: string, data: any) =>
    api.patch(`${BASE}/specifications/${specNumber}/`, data).then(r => r.data),

  // Alteration History
  listAlterations: (params?: Record<string, string>) =>
    api.get(`${BASE}/alteration-history/`, { params }).then(r => r.data),

  // Controlling Agencies
  listAgencies: () =>
    api.get(`${BASE}/agencies/`).then(r => r.data),
};

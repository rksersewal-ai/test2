import api from '../api/axios';

const BASE = '/pl-master';

export const plMasterService = {
  listPL: (params?: Record<string, string>) =>
    api.get(`${BASE}/`, { params }).then(response => response.data),

  getPL: (plNumber: string) =>
    api.get(`${BASE}/${plNumber}/`).then(response => response.data),

  createPL: (data: Record<string, unknown>) =>
    api.post(`${BASE}/`, data).then(response => response.data),

  updatePL: (plNumber: string, data: Record<string, unknown>) =>
    api.patch(`${BASE}/${plNumber}/`, data).then(response => response.data),

  deletePL: (plNumber: string) =>
    api.delete(`${BASE}/${plNumber}/`).then(response => response.data),

  getBOMTree: (plNumber: string, maxDepth = 5) =>
    api.get(`${BASE}/${plNumber}/bom/`, { params: { max_depth: maxDepth } }).then(response => response.data),

  listDrawings: (params?: Record<string, string>) =>
    api.get(`${BASE}/drawings/`, { params }).then(response => response.data),

  getDrawing: (drawingNumber: string) =>
    api.get(`${BASE}/drawings/${drawingNumber}/`).then(response => response.data),

  createDrawing: (data: Record<string, unknown>) =>
    api.post(`${BASE}/drawings/`, data).then(response => response.data),

  updateDrawing: (drawingNumber: string, data: Record<string, unknown>) =>
    api.patch(`${BASE}/drawings/${drawingNumber}/`, data).then(response => response.data),

  listSpecs: (params?: Record<string, string>) =>
    api.get(`${BASE}/specs/`, { params }).then(response => response.data),

  getSpec: (specNumber: string) =>
    api.get(`${BASE}/specs/${specNumber}/`).then(response => response.data),

  createSpec: (data: Record<string, unknown>) =>
    api.post(`${BASE}/specs/`, data).then(response => response.data),

  updateSpec: (specNumber: string, data: Record<string, unknown>) =>
    api.patch(`${BASE}/specs/${specNumber}/`, data).then(response => response.data),

  listAlterations: (params?: Record<string, string>) =>
    api.get(`${BASE}/alteration-history/`, { params }).then(response => response.data),

  listAgencies: () =>
    api.get(`${BASE}/agencies/`).then(response => response.data),
};

// =============================================================================
// FILE: frontend/src/services/plMasterService.ts
// ADDED: VendorInfo + LinkedDocuments API methods
// =============================================================================
import api from '../api/axios';

const BASE = '/pl-master';

export const plMasterService = {
  // ── PL Master ──────────────────────────────────────────────────────────────
  listPL     : (params?: Record<string,string>) => api.get(`${BASE}/`, {params}).then(r=>r.data),
  getPL      : (pl: string) => api.get(`${BASE}/${pl}/`).then(r=>r.data),
  createPL   : (data: any)  => api.post(`${BASE}/`, data).then(r=>r.data),
  updatePL   : (pl: string, data: any) => api.patch(`${BASE}/${pl}/`, data).then(r=>r.data),
  deletePL   : (pl: string) => api.delete(`${BASE}/${pl}/`),
  getBOMTree : (pl: string, maxDepth=5) => api.get(`${BASE}/${pl}/bom/`,{params:{max_depth:maxDepth}}).then(r=>r.data),

  // ── Drawings ────────────────────────────────────────────────────────────────
  listDrawings  : (params?: Record<string,string>) => api.get(`${BASE}/drawings/`,{params}).then(r=>r.data),
  getDrawing    : (dn: string) => api.get(`${BASE}/drawings/${dn}/`).then(r=>r.data),
  createDrawing : (data: any)  => api.post(`${BASE}/drawings/`,data).then(r=>r.data),
  updateDrawing : (dn: string, data: any) => api.patch(`${BASE}/drawings/${dn}/`,data).then(r=>r.data),

  // ── Specifications ──────────────────────────────────────────────────────────
  listSpecs  : (params?: Record<string,string>) => api.get(`${BASE}/specifications/`,{params}).then(r=>r.data),
  getSpec    : (sn: string) => api.get(`${BASE}/specifications/${sn}/`).then(r=>r.data),
  createSpec : (data: any)  => api.post(`${BASE}/specifications/`,data).then(r=>r.data),
  updateSpec : (sn: string, data: any) => api.patch(`${BASE}/specifications/${sn}/`,data).then(r=>r.data),

  // ── Alteration History ──────────────────────────────────────────────────────
  listAlterations: (params?: Record<string,string>) => api.get(`${BASE}/alteration-history/`,{params}).then(r=>r.data),

  // ── Controlling Agencies ────────────────────────────────────────────────────
  listAgencies: () => api.get(`${BASE}/agencies/`).then(r=>r.data),

  // ── Technical Evaluation Documents ─────────────────────────────────────────
  listTechEvalDocs  : (pl: string) => api.get(`${BASE}/${pl}/tech-eval-docs/`).then(r=>r.data),
  uploadTechEvalDoc : (pl: string, payload: {tender_number:string; eval_year:string; file:File}) => {
    const fd = new FormData();
    fd.append('file',          payload.file);
    fd.append('tender_number', payload.tender_number);
    fd.append('eval_year',     payload.eval_year);
    return api.post(`${BASE}/${pl}/tech-eval-docs/`, fd, {headers:{'Content-Type':'multipart/form-data'}}).then(r=>r.data);
  },
  deleteTechEvalDoc : (pl: string, docId: number) => api.delete(`${BASE}/${pl}/tech-eval-docs/${docId}/`).then(r=>r.data),

  // ── VD / NVD Vendor Info (NEW) ──────────────────────────────────────────────
  getVendorInfo   : (pl: string) => api.get(`${BASE}/${pl}/vendor-info/`).then(r=>r.data),
  saveVendorInfo  : (pl: string, data: any) => api.patch(`${BASE}/${pl}/vendor-info/`, data).then(r=>r.data),

  // ── Linked Documents (NEW) ──────────────────────────────────────────────────
  /** GET all linked docs, grouped by category */
  listLinkedDocs  : (pl: string, params?: Record<string,string>) =>
    api.get(`${BASE}/${pl}/linked-docs/`, {params}).then(r=>r.data),
  /** POST — link a document to this PL */
  linkDocument    : (pl: string, data: any) =>
    api.post(`${BASE}/${pl}/linked-docs/`, data).then(r=>r.data),
  /** DELETE — unlink */
  unlinkDocument  : (pl: string, linkId: number) =>
    api.delete(`${BASE}/${pl}/linked-docs/${linkId}/`).then(r=>r.data),
  /** Search EDMS documents to link */
  searchDocsToLink: (pl: string, q: string) =>
    api.get(`${BASE}/${pl}/linked-docs/search/`, {params:{q}}).then(r=>r.data),
};

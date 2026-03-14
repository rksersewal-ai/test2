// =============================================================================
// FILE: frontend/src/services/plMasterService.ts
// ADDED: Technical Evaluation Document API methods
//   listTechEvalDocs  — GET  /pl-master/{pl}/tech-eval-docs/
//   uploadTechEvalDoc — POST /pl-master/{pl}/tech-eval-docs/  (multipart)
//   deleteTechEvalDoc — DELETE /pl-master/{pl}/tech-eval-docs/{id}/
// =============================================================================
import api from '../api/axios';

const BASE = '/pl-master';

export const plMasterService = {
  // ── PL Master ───────────────────────────────────────────────────────────────
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

  // ── Drawings ─────────────────────────────────────────────────────────────
  listDrawings: (params?: Record<string, string>) =>
    api.get(`${BASE}/drawings/`, { params }).then(r => r.data),
  getDrawing: (drawingNumber: string) =>
    api.get(`${BASE}/drawings/${drawingNumber}/`).then(r => r.data),
  createDrawing: (data: any) =>
    api.post(`${BASE}/drawings/`, data).then(r => r.data),
  updateDrawing: (drawingNumber: string, data: any) =>
    api.patch(`${BASE}/drawings/${drawingNumber}/`, data).then(r => r.data),

  // ── Specifications ──────────────────────────────────────────────────────────
  listSpecs: (params?: Record<string, string>) =>
    api.get(`${BASE}/specifications/`, { params }).then(r => r.data),
  getSpec: (specNumber: string) =>
    api.get(`${BASE}/specifications/${specNumber}/`).then(r => r.data),
  createSpec: (data: any) =>
    api.post(`${BASE}/specifications/`, data).then(r => r.data),
  updateSpec: (specNumber: string, data: any) =>
    api.patch(`${BASE}/specifications/${specNumber}/`, data).then(r => r.data),

  // ── Alteration History ───────────────────────────────────────────────────────
  listAlterations: (params?: Record<string, string>) =>
    api.get(`${BASE}/alteration-history/`, { params }).then(r => r.data),

  // ── Controlling Agencies ─────────────────────────────────────────────────────
  listAgencies: () =>
    api.get(`${BASE}/agencies/`).then(r => r.data),

  // ── Technical Evaluation Documents (NEW) ──────────────────────────────
  /**
   * GET /pl-master/{plNumber}/tech-eval-docs/
   * Returns list of up to 3 uploaded evaluation documents for this PL.
   */
  listTechEvalDocs: (plNumber: string) =>
    api.get(`${BASE}/${plNumber}/tech-eval-docs/`).then(r => r.data),

  /**
   * POST /pl-master/{plNumber}/tech-eval-docs/
   * Uploads a new evaluation document (PDF or DOCX).
   * Sends multipart/form-data with: file, tender_number, eval_year
   */
  uploadTechEvalDoc: (
    plNumber    : string,
    payload     : { tender_number: string; eval_year: string; file: File }
  ) => {
    const fd = new FormData();
    fd.append('file',          payload.file);
    fd.append('tender_number', payload.tender_number);
    fd.append('eval_year',     payload.eval_year);
    return api.post(
      `${BASE}/${plNumber}/tech-eval-docs/`,
      fd,
      { headers: { 'Content-Type': 'multipart/form-data' } }
    ).then(r => r.data);
  },

  /**
   * DELETE /pl-master/{plNumber}/tech-eval-docs/{id}/
   */
  deleteTechEvalDoc: (plNumber: string, docId: number) =>
    api.delete(`${BASE}/${plNumber}/tech-eval-docs/${docId}/`).then(r => r.data),
};

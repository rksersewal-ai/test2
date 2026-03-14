// =============================================================================
// FILE: frontend/src/services/prototypeService.ts  (Phase 6 — corrected URLs)
// Matches Django prototype.urls:
//   /api/prototype/inspections/                       → list/create
//   /api/prototype/inspections/:id/                   → retrieve/update
//   /api/prototype/inspections/:id/close/             → close action
//   /api/prototype/inspections/:id/punch-items/       → add punch item
//   /api/prototype/punch-items/:id/close/             → close punch item
// =============================================================================
import api from '../api/axios';
import type { PaginatedResponse } from '../api/types';
import type { Inspection, PunchItem } from '../types/prototype';

const BASE = '/prototype';

export const prototypeService = {
  // ---- Inspections ----------------------------------------------------------
  listInspections: (params?: Record<string, string>) =>
    api.get<PaginatedResponse<Inspection>>(`${BASE}/inspections/`, { params }).then(r => r.data),

  getInspection: (id: number) =>
    api.get<Inspection>(`${BASE}/inspections/${id}/`).then(r => r.data),

  createInspection: (data: Partial<Inspection>) =>
    api.post<Inspection>(`${BASE}/inspections/`, data).then(r => r.data),

  updateInspection: (id: number, data: Partial<Inspection>) =>
    api.patch<Inspection>(`${BASE}/inspections/${id}/`, data).then(r => r.data),

  closeInspection: (id: number) =>
    api.post<Inspection>(`${BASE}/inspections/${id}/close/`).then(r => r.data),

  // ---- Punch Items ----------------------------------------------------------
  // Add punch item to an inspection
  addPunchItem: (inspectionId: number, data: Partial<PunchItem>) =>
    api.post<PunchItem>(`${BASE}/inspections/${inspectionId}/punch-items/`, data).then(r => r.data),

  // Close a punch item (standalone endpoint — correct URL vs old stub)
  closePunchItem: (punchId: number, remarks?: string) =>
    api.post<PunchItem>(`${BASE}/punch-items/${punchId}/close/`, { remarks }).then(r => r.data),

  // Fetch all punch items for an inspection (from nested list)
  listPunchItems: (inspectionId: number, params?: Record<string, string>) =>
    api.get<PaginatedResponse<PunchItem>>(`${BASE}/punch-items/`, {
      params: { inspection: inspectionId, ...params }
    }).then(r => r.data),
};

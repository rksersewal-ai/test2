// =============================================================================
// FILE: frontend/src/services/configService.ts  (Phase 6 — corrected URLs)
// Matches Django config_mgmt.urls:
//   /api/config/configs/          → LocoConfig CRUD
//   /api/config/ecn/              → ECN CRUD
//   /api/config/ecn/:id/approve/  → approve action
//   /api/config/ecn/:id/reject/   → reject action
// =============================================================================
import api from '../api/axios';
import type { PaginatedResponse } from '../api/types';
import type { LocoConfig, ECN } from '../types/config';

const BASE = '/config';

export const configService = {
  // ---- Loco Configurations --------------------------------------------------
  listConfigs: (params?: Record<string, string>) =>
    api.get<PaginatedResponse<LocoConfig>>(`${BASE}/configs/`, { params }).then(r => r.data),

  getConfig: (id: number) =>
    api.get<LocoConfig>(`${BASE}/configs/${id}/`).then(r => r.data),

  createConfig: (data: Partial<LocoConfig>) =>
    api.post<LocoConfig>(`${BASE}/configs/`, data).then(r => r.data),

  updateConfig: (id: number, data: Partial<LocoConfig>) =>
    api.patch<LocoConfig>(`${BASE}/configs/${id}/`, data).then(r => r.data),

  deleteConfig: (id: number) =>
    api.delete(`${BASE}/configs/${id}/`),

  // ---- ECN Register ---------------------------------------------------------
  listECN: (params?: Record<string, string>) =>
    api.get<PaginatedResponse<ECN>>(`${BASE}/ecn/`, { params }).then(r => r.data),

  getECN: (id: number) =>
    api.get<ECN>(`${BASE}/ecn/${id}/`).then(r => r.data),

  createECN: (data: Partial<ECN>) =>
    api.post<ECN>(`${BASE}/ecn/`, data).then(r => r.data),

  updateECN: (id: number, data: Partial<ECN>) =>
    api.patch<ECN>(`${BASE}/ecn/${id}/`, data).then(r => r.data),

  approveECN: (id: number) =>
    api.post<ECN>(`${BASE}/ecn/${id}/approve/`).then(r => r.data),

  rejectECN: (id: number, reason: string) =>
    api.post<ECN>(`${BASE}/ecn/${id}/reject/`, { reason }).then(r => r.data),
};

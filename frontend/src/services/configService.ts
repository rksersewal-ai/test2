// =============================================================================
// FILE: frontend/src/services/configService.ts
// Config Management API — loco configs, ECN records, BOM diffs
// =============================================================================
import api from '../api/axios';

const BASE = '/config';

export const configService = {
  // Loco configurations
  listConfigs: (params?: Record<string, string>) =>
    api.get(`${BASE}/loco-configs/`, { params }).then(r => r.data),
  getConfig: (id: number) =>
    api.get(`${BASE}/loco-configs/${id}/`).then(r => r.data),
  createConfig: (data: any) =>
    api.post(`${BASE}/loco-configs/`, data).then(r => r.data),
  updateConfig: (id: number, data: any) =>
    api.patch(`${BASE}/loco-configs/${id}/`, data).then(r => r.data),
  deleteConfig: (id: number) =>
    api.delete(`${BASE}/loco-configs/${id}/`),

  // ECN (Engineering Change Notice)
  listECN: (params?: Record<string, string>) =>
    api.get(`${BASE}/ecn/`, { params }).then(r => r.data),
  getECN: (id: number) =>
    api.get(`${BASE}/ecn/${id}/`).then(r => r.data),
  createECN: (data: any) =>
    api.post(`${BASE}/ecn/`, data).then(r => r.data),
  approveECN: (id: number) =>
    api.post(`${BASE}/ecn/${id}/approve/`).then(r => r.data),

  // BOM diff between two config versions
  bomDiff: (configA: number, configB: number) =>
    api.get(`${BASE}/bom-diff/`, { params: { config_a: configA, config_b: configB } }).then(r => r.data),

  // Loco type master list
  listLocoTypes: () =>
    api.get(`${BASE}/loco-types/`).then(r => r.data),
};

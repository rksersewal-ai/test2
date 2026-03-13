// =============================================================================
// FILE: frontend/src/services/dropdownApi.ts
// PURPOSE: API client for dropdown public + admin endpoints
// =============================================================================
import type { DropdownItem, DropdownGroup, DropdownCreatePayload, DropdownUpdatePayload } from '../types/dropdown';

const BASE_PUBLIC = '/api/dropdowns';
const BASE_ADMIN  = '/api/admin/dropdowns';

async function apiFetch<T>(url: string, options?: RequestInit): Promise<T> {
  const token = localStorage.getItem('access_token');
  const res = await fetch(url, {
    headers: {
      'Content-Type': 'application/json',
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
    },
    ...options,
  });
  if (!res.ok) throw new Error(`API error ${res.status}: ${await res.text()}`);
  if (res.status === 204) return undefined as T;
  return res.json();
}

export const dropdownApi = {
  // ---- Public (all users) ----
  getAllGroups(): Promise<DropdownGroup[]> {
    return apiFetch(`${BASE_PUBLIC}/`);
  },
  getGroup(groupKey: string): Promise<DropdownItem[]> {
    return apiFetch(`${BASE_PUBLIC}/${groupKey}/`);
  },

  // ---- Admin only ----
  adminListGroup(groupKey: string): Promise<DropdownItem[]> {
    return apiFetch(`${BASE_ADMIN}/${groupKey}/`);
  },
  adminCreate(groupKey: string, payload: DropdownCreatePayload): Promise<DropdownItem> {
    return apiFetch(`${BASE_ADMIN}/${groupKey}/`, {
      method: 'POST',
      body: JSON.stringify(payload),
    });
  },
  adminUpdate(groupKey: string, itemId: number, payload: DropdownUpdatePayload): Promise<DropdownItem> {
    return apiFetch(`${BASE_ADMIN}/${groupKey}/${itemId}/`, {
      method: 'PATCH',
      body: JSON.stringify(payload),
    });
  },
  adminDeactivate(groupKey: string, itemId: number): Promise<void> {
    return apiFetch(`${BASE_ADMIN}/${groupKey}/${itemId}/?deactivate=1`, { method: 'DELETE' });
  },
  adminDelete(groupKey: string, itemId: number): Promise<void> {
    return apiFetch(`${BASE_ADMIN}/${groupKey}/${itemId}/`, { method: 'DELETE' });
  },
  getAuditLog(groupKey: string): Promise<any[]> {
    return apiFetch(`${BASE_ADMIN}/${groupKey}/audit-log/`);
  },
};

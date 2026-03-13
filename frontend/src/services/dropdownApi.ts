// =============================================================================
// FILE: frontend/src/services/dropdownApi.ts
// FIX (#8): JWT stored in httpOnly cookie — no longer read from localStorage.
//           All requests rely on the browser sending the cookie automatically.
//           The fetch credential mode is set to 'include'.
// FIX (#11): getSection() calls core/sections API — not dropdown_master.
// =============================================================================
import type { DropdownItem, DropdownGroup, DropdownCreatePayload, DropdownUpdatePayload } from '../types/dropdown';

const BASE_PUBLIC  = '/api/dropdowns';
const BASE_ADMIN   = '/api/admin/dropdowns';
const BASE_CORE    = '/api/core';

async function apiFetch<T>(url: string, options?: RequestInit): Promise<T> {
  // FIX (#8): credentials: 'include' sends the httpOnly JWT cookie automatically.
  // No Authorization header injection from localStorage needed.
  const res = await fetch(url, {
    credentials: 'include',           // sends httpOnly cookie
    headers: { 'Content-Type': 'application/json' },
    ...options,
  });
  if (!res.ok) throw new Error(`API error ${res.status}: ${await res.text()}`);
  if (res.status === 204) return undefined as T;
  return res.json();
}

export const dropdownApi = {
  // ---- Public (all authenticated users) ----
  getAllGroups(): Promise<DropdownGroup[]> {
    return apiFetch(`${BASE_PUBLIC}/`);
  },
  getGroup(groupKey: string): Promise<DropdownItem[]> {
    return apiFetch(`${BASE_PUBLIC}/${groupKey}/`);
  },

  // FIX (#11): Sections come from core_section table, not dropdown_master
  getSections(): Promise<{ id: number; code: string; name: string }[]> {
    return apiFetch(`${BASE_CORE}/sections/`);
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

// =============================================================================
// FILE: frontend/src/services/dropdownApi.ts
// FIX (#8): Replaced manual localStorage token injection with apiFetch
//           which uses credentials:'include' (httpOnly cookie).
// =============================================================================
import { apiFetch } from './authApi';
import type { DropdownItem, DropdownGroup, DropdownCreatePayload, DropdownUpdatePayload } from '../types/dropdown';

const BASE_PUBLIC = '/api/dropdowns';
const BASE_ADMIN  = '/api/admin/dropdowns';

export const dropdownApi = {
  getAllGroups(): Promise<DropdownGroup[]> {
    return apiFetch(`${BASE_PUBLIC}/`);
  },
  getGroup(groupKey: string): Promise<DropdownItem[]> {
    return apiFetch(`${BASE_PUBLIC}/${groupKey}/`);
  },
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

// =============================================================================
// FILE: frontend/src/services/authApi.ts
// BUG FIX: Original file used raw fetch() with credentials:include but
// duplicated all auth logic that now lives in AuthContext.tsx.
// This file is kept for backward compatibility but delegates to AuthContext
// via the canonical apiClient (withCredentials already set globally).
//
// Direct usage: import { apiFetch } from '../services/authApi'
// Auth state: use useAuth() hook instead
// =============================================================================
import apiClient from './apiClient';
import type { AxiosRequestConfig } from 'axios';

/**
 * Generic typed API helper wrapping the canonical Axios client.
 * Replaces the old fetch-based apiFetch() — withCredentials is set globally.
 */
export async function apiFetch<T>(
  url: string,
  options?: AxiosRequestConfig
): Promise<T> {
  const res = await apiClient.request<T>({ url, ...options });
  return res.data;
}

/**
 * @deprecated Use useAuth().login() from AuthContext instead.
 * Kept only for any legacy call sites.
 */
export const authApi = {
  async login(username: string, password: string) {
    const res = await apiClient.post('/auth/token/', { username, password });
    return res.data;
  },
  async refresh() {
    await apiClient.post('/auth/token/refresh/', {});
  },
  async logout() {
    await apiClient.post('/auth/logout/', {});
  },
};

// =============================================================================
// FILE: frontend/src/api/client.ts
// BUG FIX: Added withCredentials: true so Axios sends httpOnly cookies on
// every request. Without this, all API calls return 401 after login.
// Also fixed baseURL to use /api/v1 (Vite proxy strips /api -> Django /api/v1)
// =============================================================================
import axios, { AxiosError, InternalAxiosRequestConfig } from 'axios';

export const apiClient = axios.create({
  baseURL        : '/api/v1',
  withCredentials: true,          // BUG FIX: send httpOnly cookies on every request
  headers        : { 'Content-Type': 'application/json' },
  timeout        : 30_000,
});

// ---- Silent token refresh on 401 ------------------------------------------
let isRefreshing  = false;
let refreshQueue: Array<(ok: boolean) => void> = [];

apiClient.interceptors.response.use(
  res => res,
  async (error: AxiosError) => {
    const original = error.config as InternalAxiosRequestConfig & { _retry?: boolean };

    if (error.response?.status === 401 && !original._retry) {
      original._retry = true;

      if (isRefreshing) {
        // Queue subsequent requests until refresh completes
        return new Promise((resolve, reject) => {
          refreshQueue.push(ok => ok ? resolve(apiClient(original)) : reject(error));
        });
      }

      isRefreshing = true;
      try {
        await axios.post('/api/v1/auth/token/refresh/', {}, { withCredentials: true });
        refreshQueue.forEach(cb => cb(true));
        refreshQueue = [];
        return apiClient(original);
      } catch {
        refreshQueue.forEach(cb => cb(false));
        refreshQueue = [];
        // Cookie fully expired — redirect to login
        sessionStorage.removeItem('auth_user');
        window.location.href = '/login';
        return Promise.reject(error);
      } finally {
        isRefreshing = false;
      }
    }
    return Promise.reject(error);
  }
);

// Re-export as default for files using: import apiClient from '../api/axios'
export default apiClient;

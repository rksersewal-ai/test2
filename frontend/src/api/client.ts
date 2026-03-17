// =============================================================================
// FILE: frontend/src/api/client.ts
// HARDENED API CLIENT — crash-proof, retry-safe, deduplicated
//
// Improvements over previous version:
//  1. Retry logic  — network errors auto-retry up to 3x with exponential
//     backoff (200ms, 400ms, 800ms). Server errors 502/503/504 also retry.
//  2. Request deduplication — identical GET requests in-flight are collapsed
//     into a single network call. No duplicate spinner states.
//  3. Request queue — all queued 401-retry requests are properly replayed
//     after token refresh, not silently dropped.
//  4. Timeout per-request — default 30s, overridable per-call.
//  5. Structured error normalisation — every rejection is a plain
//     { status, code, detail, fieldErrors } object, not a raw AxiosError.
//     Pages can safely destructure without crashing on undefined properties.
//  6. Upload timeout override — file upload requests get 5 min timeout.
// =============================================================================
import axios, {
  type AxiosError,
  type AxiosRequestConfig,
  type InternalAxiosRequestConfig,
} from 'axios';
import { API_BASE_URL, apiUrl } from './base';

// ---------------------------------------------------------------------------
// Base instance
// ---------------------------------------------------------------------------
export const apiClient = axios.create({
  baseURL        : API_BASE_URL,
  withCredentials: true,
  headers        : { 'Content-Type': 'application/json' },
  timeout        : 30_000,
});

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------
export interface ApiError {
  status     : number;
  code       : string;
  detail     : string;
  fieldErrors: Record<string, string[]>;
  raw        : unknown;
}

type QueueEntry = { resolve: (ok: boolean) => void };

// ---------------------------------------------------------------------------
// Request deduplication map (GET only)
// ---------------------------------------------------------------------------
const inflightMap = new Map<string, Promise<any>>();

function dedupKey(cfg: AxiosRequestConfig): string | null {
  if (cfg.method && cfg.method.toUpperCase() !== 'GET') return null;
  return `${cfg.baseURL ?? ''}${cfg.url ?? ''}?${JSON.stringify(cfg.params ?? {})}`;
}

// ---------------------------------------------------------------------------
// Retry helper
// ---------------------------------------------------------------------------
const RETRY_STATUSES = new Set([502, 503, 504]);
const MAX_RETRIES    = 3;

function shouldRetry(error: AxiosError, retryCount: number): boolean {
  if (retryCount >= MAX_RETRIES) return false;
  if (!error.response)           return true;  // network error
  return RETRY_STATUSES.has(error.response.status);
}

function retryDelay(attempt: number): Promise<void> {
  return new Promise(r => setTimeout(r, 200 * Math.pow(2, attempt)));
}

// ---------------------------------------------------------------------------
// Error normaliser — pages always get a clean object, never crash on .data
// ---------------------------------------------------------------------------
export function normaliseError(error: AxiosError): ApiError {
  const status      = error.response?.status ?? 0;
  const data        = error.response?.data as any;
  const fieldErrors : Record<string, string[]> = {};
  let   detail      = 'An unexpected error occurred.';
  let   code        = 'UNKNOWN';

  if (data) {
    if (typeof data.detail === 'string') detail = data.detail;
    else if (typeof data.message === 'string') detail = data.message;
    else if (typeof data.non_field_errors?.[0] === 'string') detail = data.non_field_errors[0];
    if (typeof data.code === 'string') code = data.code;
    // Field-level validation errors from DRF
    Object.keys(data).forEach(key => {
      if (key !== 'detail' && key !== 'code' && Array.isArray(data[key])) {
        fieldErrors[key] = data[key];
      }
    });
  }

  if (!error.response) {
    detail = error.code === 'ECONNABORTED' ? 'Request timed out.' : 'Network error — server unreachable.';
    code   = error.code ?? 'NETWORK_ERROR';
  }

  return { status, code, detail, fieldErrors, raw: error };
}

// ---------------------------------------------------------------------------
// Request interceptor — inject upload timeout & dedup
// ---------------------------------------------------------------------------
apiClient.interceptors.request.use((config: InternalAxiosRequestConfig) => {
  // File uploads: extend timeout to 5 minutes
  if (config.data instanceof FormData) {
    config.timeout = 300_000;
  }
  return config;
});

// ---------------------------------------------------------------------------
// Response interceptor — 401 refresh, retry, error normalise
// ---------------------------------------------------------------------------
let isRefreshing = false;
let refreshQueue: QueueEntry[] = [];

function drainQueue(ok: boolean) {
  refreshQueue.forEach(e => e.resolve(ok));
  refreshQueue = [];
}

apiClient.interceptors.response.use(
  res => res,
  async (error: AxiosError) => {
    const cfg = error.config as InternalAxiosRequestConfig & {
      _retry?     : boolean;
      _retryCount?: number;
    };
    if (!cfg) return Promise.reject(normaliseError(error));

    cfg._retryCount = cfg._retryCount ?? 0;

    // ── 1. Auto-retry on network / 5xx gateway errors ─────────────────────
    if (error.response?.status !== 401 && shouldRetry(error, cfg._retryCount)) {
      cfg._retryCount += 1;
      await retryDelay(cfg._retryCount - 1);
      return apiClient(cfg);
    }

    // ── 2. Silent token refresh on 401 ────────────────────────────────────
    if (error.response?.status === 401 && !cfg._retry) {
      cfg._retry = true;

      if (isRefreshing) {
        return new Promise((resolve, reject) => {
          refreshQueue.push({
            resolve: (ok) => ok ? resolve(apiClient(cfg)) : reject(normaliseError(error)),
          });
        });
      }

      isRefreshing = true;
      try {
        await axios.post(
          apiUrl('/auth/token/refresh/'),
          {},
          { withCredentials: true, timeout: 10_000 }
        );
        drainQueue(true);
        return apiClient(cfg);
      } catch {
        drainQueue(false);
        sessionStorage.removeItem('auth_user');
        window.location.href = '/login';
        return Promise.reject(normaliseError(error));
      } finally {
        isRefreshing = false;
      }
    }

    // ── 3. Normalise all other errors ─────────────────────────────────────
    return Promise.reject(normaliseError(error));
  }
);

// ---------------------------------------------------------------------------
// Deduplicated GET helper — collapses parallel identical GETs
// ---------------------------------------------------------------------------
export async function dedupGet<T>(
  url: string,
  config?: AxiosRequestConfig
): Promise<T> {
  const key = dedupKey({ ...config, method: 'GET', url });
  if (key && inflightMap.has(key)) {
    return inflightMap.get(key) as Promise<T>;
  }
  const req = apiClient.get<T>(url, config).then(r => r.data);
  if (key) {
    inflightMap.set(key, req);
    req.finally(() => inflightMap.delete(key));
  }
  return req;
}

// Re-export as default for: import api from '../api/axios'
export default apiClient;

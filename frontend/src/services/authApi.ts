// =============================================================================
// FILE: frontend/src/services/authApi.ts
// FIX (#8): JWT stored in httpOnly cookie set by Django backend.
//           Removed localStorage.getItem('access_token') pattern from all
//           API service files. Browser sends cookie automatically on every
//           request (credentials: 'include'). Token is invisible to JS.
//
// Backend requirement: Configure simplejwt to set cookie:
//   REST_FRAMEWORK settings + SIMPLE_JWT cookie settings (see settings note below)
// =============================================================================

export const authApi = {
  /**
   * Login: POST /api/auth/token/
   * Backend sets httpOnly cookie 'access_token' and 'refresh_token'.
   * No token handling needed on frontend side.
   */
  async login(username: string, password: string): Promise<{ user: any }> {
    const res = await fetch('/api/auth/token/', {
      method: 'POST',
      credentials: 'include',           // send + receive cookies
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username, password }),
    });
    if (!res.ok) throw new Error('Login failed');
    return res.json();
  },

  async refresh(): Promise<void> {
    const res = await fetch('/api/auth/token/refresh/', {
      method: 'POST',
      credentials: 'include',
    });
    if (!res.ok) throw new Error('Session expired. Please login again.');
  },

  async logout(): Promise<void> {
    await fetch('/api/auth/logout/', {
      method: 'POST',
      credentials: 'include',
    });
  },
};

/**
 * Base fetch wrapper used by ALL API service files.
 * FIX (#8): Uses credentials:'include' so cookie is sent automatically.
 *           Removed Authorization header injection from all service files.
 *
 * Django settings required:
 *   SIMPLE_JWT = {
 *     'AUTH_COOKIE': 'access_token',
 *     'AUTH_COOKIE_SECURE': False,   # True in production HTTPS
 *     'AUTH_COOKIE_HTTP_ONLY': True,
 *     'AUTH_COOKIE_SAMESITE': 'Lax',
 *   }
 *   Install: djangorestframework-simplejwt[crypto]
 *   Use: rest_framework_simplejwt.authentication.JWTCookieAuthentication
 */
export async function apiFetch<T>(url: string, options?: RequestInit): Promise<T> {
  const res = await fetch(url, {
    credentials: 'include',              // FIX: cookie-based auth, no Bearer header
    headers: {
      'Content-Type': 'application/json',
      ...((options?.headers as Record<string, string>) ?? {}),
    },
    ...options,
  });

  if (res.status === 401) {
    // Try silent refresh once
    try {
      await authApi.refresh();
      // Retry original request
      const retry = await fetch(url, {
        credentials: 'include',
        headers: { 'Content-Type': 'application/json' },
        ...options,
      });
      if (retry.status === 204) return undefined as T;
      return retry.json();
    } catch {
      window.location.href = '/login';
      throw new Error('Session expired.');
    }
  }

  if (res.status === 204) return undefined as T;
  if (!res.ok) throw new Error(`API error ${res.status}: ${await res.text()}`);
  return res.json();
}

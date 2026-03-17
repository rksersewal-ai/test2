// =============================================================================
// FILE: frontend/src/context/AuthContext.tsx
//
// BUG FIXES:
//   1. Removed localStorage.getItem('access_token') — tokens are now httpOnly
//      cookies, invisible to JS. Storage of raw tokens was a security bug.
//   2. login() now reads user profile from JSON body (not from token fields).
//   3. logout() calls POST /api/v1/auth/logout/ to clear server-side cookies.
//   4. Session restore: reads 'auth_user' from sessionStorage only (no token
//      check — cookie presence is handled transparently by the browser).
//   5. Added /api/v1/auth/me/ silent-check on mount to verify session is live.
// =============================================================================
import { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import type { TokenResponse } from '../api/types';
import { apiUrl } from '../api/base';

type UserInfo = Omit<TokenResponse, 'access' | 'refresh'>;

interface AuthState {
  isAuthenticated : boolean;
  user            : UserInfo | null;
  login           : (username: string, password: string) => Promise<void>;
  logout          : () => Promise<void>;
}

const AuthContext = createContext<AuthState | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<UserInfo | null>(() => {
    // Restore from sessionStorage on hard refresh (safe — no tokens stored)
    try {
      const stored = sessionStorage.getItem('auth_user');
      return stored ? JSON.parse(stored) : null;
    } catch { return null; }
  });

  // On mount: silently verify the live session against the backend.
  useEffect(() => {
    if (!user) return;
    fetch(apiUrl('/auth/me/'), {
      method: 'GET',
      credentials: 'include',
    }).then(res => {
      if (!res.ok) {
        sessionStorage.removeItem('auth_user');
        setUser(null);
      }
    }).catch(() => {
      // Network error on startup — keep user state, will retry on next API call
    });
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const login = async (username: string, password: string): Promise<void> => {
    const res = await fetch(apiUrl('/auth/token/'), {
      method: 'POST',
      credentials: 'include',          // receive httpOnly cookies
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username, password }),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || 'Invalid username or password');
    }
    const data: TokenResponse = await res.json();
    const userInfo: UserInfo = {
      full_name : data.full_name,
      username  : data.username,
      email     : data.email,
      is_staff  : data.is_staff,
      role      : data.role,
      section   : data.section,
    };
    sessionStorage.setItem('auth_user', JSON.stringify(userInfo));
    setUser(userInfo);
  };

  const logout = async (): Promise<void> => {
    try {
      await fetch(apiUrl('/auth/logout/'), {
        method: 'POST',
        credentials: 'include',        // sends cookies so server can clear them
      });
    } catch { /* ignore network errors on logout */ }
    sessionStorage.removeItem('auth_user');
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ isAuthenticated: !!user, user, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuthContext() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuthContext must be inside AuthProvider');
  return ctx;
}

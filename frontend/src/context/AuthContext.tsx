import { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { apiClient } from '../api/client';
import type { TokenResponse } from '../api/types';

interface AuthState {
  isAuthenticated: boolean;
  user: Omit<TokenResponse, 'access' | 'refresh'> | null;
  login: (username: string, password: string) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthState | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<AuthState['user']>(null);

  useEffect(() => {
    const stored = localStorage.getItem('auth_user');
    const token = localStorage.getItem('access_token');
    if (stored && token) setUser(JSON.parse(stored));
  }, []);

  const login = async (username: string, password: string) => {
    const { data } = await apiClient.post<TokenResponse>('/auth/token/', { username, password });
    localStorage.setItem('access_token', data.access);
    localStorage.setItem('refresh_token', data.refresh);
    const userInfo = {
      user_id: data.user_id,
      username: data.username,
      full_name: data.full_name,
      role: data.role,
      section_id: data.section_id,
      section_name: data.section_name,
    };
    localStorage.setItem('auth_user', JSON.stringify(userInfo));
    setUser(userInfo);
  };

  const logout = () => {
    localStorage.clear();
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

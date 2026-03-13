// =============================================================================
// FILE: frontend/src/context/ThemeContext.tsx
// SPRINT 3 — Feature #10: Dark Mode
// PURPOSE : Provides a ThemeContext that persists the user's light/dark
//           preference to localStorage and applies data-theme on <html>.
//           Respects OS-level prefers-color-scheme on first visit.
// =============================================================================
import React, {
  createContext, useContext, useEffect, useState, ReactNode,
} from 'react';

type Theme = 'light' | 'dark';

interface ThemeContextValue {
  theme:      Theme;
  isDark:     boolean;
  toggleTheme: () => void;
  setTheme:   (t: Theme) => void;
}

const ThemeContext = createContext<ThemeContextValue | null>(null);

const STORAGE_KEY = 'edms_theme';

function resolveInitialTheme(): Theme {
  const stored = localStorage.getItem(STORAGE_KEY) as Theme | null;
  if (stored === 'light' || stored === 'dark') return stored;
  // Respect OS preference on first visit
  return window.matchMedia?.('(prefers-color-scheme: dark)').matches
    ? 'dark' : 'light';
}

export function ThemeProvider({ children }: { children: ReactNode }) {
  const [theme, setThemeState] = useState<Theme>(resolveInitialTheme);

  // Apply to <html> and persist whenever theme changes
  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem(STORAGE_KEY, theme);
  }, [theme]);

  const setTheme = (t: Theme) => setThemeState(t);
  const toggleTheme = () => setThemeState(prev => prev === 'dark' ? 'light' : 'dark');

  return (
    <ThemeContext.Provider value={{ theme, isDark: theme === 'dark', toggleTheme, setTheme }}>
      {children}
    </ThemeContext.Provider>
  );
}

export function useTheme(): ThemeContextValue {
  const ctx = useContext(ThemeContext);
  if (!ctx) throw new Error('useTheme must be used inside <ThemeProvider>');
  return ctx;
}

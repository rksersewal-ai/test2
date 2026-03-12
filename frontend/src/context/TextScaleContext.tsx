/**
 * TextScaleContext — A+ / A- / Reset text scaling
 * Persisted in localStorage. Applied via CSS --text-scale variable on <html>.
 */
import { createContext, useContext, useState, useEffect, ReactNode } from 'react';

export type ScaleLevel = 'small' | 'default' | 'large' | 'xlarge';

const SCALE_MAP: Record<ScaleLevel, number> = {
  small:   0.90,
  default: 1.00,
  large:   1.10,
  xlarge:  1.20,
};

const SCALE_ORDER: ScaleLevel[] = ['small', 'default', 'large', 'xlarge'];

const LS_KEY = 'edms_text_scale';

interface TextScaleState {
  level: ScaleLevel;
  increase: () => void;
  decrease: () => void;
  reset:    () => void;
}

const TextScaleContext = createContext<TextScaleState | null>(null);

export function TextScaleProvider({ children }: { children: ReactNode }) {
  const [level, setLevel] = useState<ScaleLevel>(() => {
    return (localStorage.getItem(LS_KEY) as ScaleLevel | null) ?? 'default';
  });

  useEffect(() => {
    document.documentElement.style.setProperty('--text-scale', String(SCALE_MAP[level]));
    localStorage.setItem(LS_KEY, level);
  }, [level]);

  const increase = () => {
    setLevel((prev) => {
      const idx = SCALE_ORDER.indexOf(prev);
      return idx < SCALE_ORDER.length - 1 ? SCALE_ORDER[idx + 1] : prev;
    });
  };

  const decrease = () => {
    setLevel((prev) => {
      const idx = SCALE_ORDER.indexOf(prev);
      return idx > 0 ? SCALE_ORDER[idx - 1] : prev;
    });
  };

  const reset = () => setLevel('default');

  return (
    <TextScaleContext.Provider value={{ level, increase, decrease, reset }}>
      {children}
    </TextScaleContext.Provider>
  );
}

export function useTextScale() {
  const ctx = useContext(TextScaleContext);
  if (!ctx) throw new Error('useTextScale must be inside TextScaleProvider');
  return ctx;
}

/**
 * Toast notification system
 * Usage: const { toast } = useToast();
 *        toast.success('Saved!', 'Document updated successfully.');
 */
import { createContext, useContext, useState, useCallback, ReactNode } from 'react';

export type ToastType = 'success' | 'error' | 'warning' | 'info';

interface ToastItem { id: string; type: ToastType; title: string; message?: string; }

const ICONS: Record<ToastType, string> = {
  success: '\u2705', error: '\u274C', warning: '\u26A0\uFE0F', info: '\u2139\uFE0F'
};

interface ToastContextValue {
  toast: {
    success: (title: string, message?: string) => void;
    error:   (title: string, message?: string) => void;
    warning: (title: string, message?: string) => void;
    info:    (title: string, message?: string) => void;
  };
}

const ToastContext = createContext<ToastContextValue | null>(null);

export function ToastProvider({ children }: { children: ReactNode }) {
  const [items, setItems] = useState<ToastItem[]>([]);

  const add = useCallback((type: ToastType, title: string, message?: string) => {
    const id = `${Date.now()}-${Math.random()}`;
    setItems((prev) => [...prev, { id, type, title, message }]);
    setTimeout(() => setItems((prev) => prev.filter((t) => t.id !== id)), 4000);
  }, []);

  const toast = {
    success: (title: string, msg?: string) => add('success', title, msg),
    error:   (title: string, msg?: string) => add('error',   title, msg),
    warning: (title: string, msg?: string) => add('warning', title, msg),
    info:    (title: string, msg?: string) => add('info',    title, msg),
  };

  return (
    <ToastContext.Provider value={{ toast }}>
      {children}
      <div className="toast-container" role="log" aria-live="polite" aria-atomic="false">
        {items.map((item) => (
          <div key={item.id} className={`toast toast-${item.type}`}>
            <span className="toast-icon">{ICONS[item.type]}</span>
            <div className="toast-body">
              <div className="toast-title">{item.title}</div>
              {item.message && <div className="toast-msg">{item.message}</div>}
            </div>
            <button
              style={{ background: 'none', border: 'none', color: 'rgba(255,255,255,0.6)', cursor: 'pointer', padding: '0 4px', fontSize: '14px' }}
              onClick={() => setItems((p) => p.filter((t) => t.id !== item.id))}
              aria-label="Dismiss"
            >\u00D7</button>
          </div>
        ))}
      </div>
    </ToastContext.Provider>
  );
}

export function useToast() {
  const ctx = useContext(ToastContext);
  if (!ctx) throw new Error('useToast must be inside ToastProvider');
  return ctx;
}

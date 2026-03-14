// =============================================================================
// Toast — transient success/error/info notification (top-right)
// Usage:
//   const [toast, setToast] = useState<ToastMsg | null>(null);
//   setToast({ type: 'success', text: 'Saved!' });
//   <Toast msg={toast} onClose={() => setToast(null)} />
// =============================================================================
import React, { useEffect } from 'react';
import './Toast.css';

export type ToastType = 'success' | 'error' | 'info' | 'warning';
export interface ToastMsg { type: ToastType; text: string; }

const ICONS: Record<ToastType, string> = {
  success: '✓',
  error:   '✕',
  info:    'ℹ',
  warning: '⚠',
};

export default function Toast({
  msg, onClose, duration = 3500,
}: {
  msg: ToastMsg | null;
  onClose: () => void;
  duration?: number;
}) {
  useEffect(() => {
    if (!msg) return;
    const t = setTimeout(onClose, duration);
    return () => clearTimeout(t);
  }, [msg, duration, onClose]);

  if (!msg) return null;
  return (
    <div className={`toast toast-${msg.type}`}>
      <span className="toast-icon">{ICONS[msg.type]}</span>
      <span className="toast-text">{msg.text}</span>
      <button className="toast-close" onClick={onClose}>✕</button>
    </div>
  );
}

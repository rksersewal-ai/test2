// =============================================================================
// FILE: frontend/src/components/common/Toast.tsx
// =============================================================================
import React, { useEffect } from 'react';
import './Toast.css';

export interface ToastMsg {
  type: 'success' | 'error' | 'info' | 'warning';
  text: string;
}

interface Props {
  msg: ToastMsg | null;
  onClose: () => void;
  duration?: number;
}

export default function Toast({ msg, onClose, duration = 3500 }: Props) {
  useEffect(() => {
    if (!msg) return;
    const t = setTimeout(onClose, duration);
    return () => clearTimeout(t);
  }, [msg, duration, onClose]);

  if (!msg) return null;

  return (
    <div
      className={`toast toast--${msg.type}`}
      role="alert"
      aria-live="assertive"
      aria-atomic="true"
    >
      <span className="toast-icon" aria-hidden="true">
        {msg.type === 'success' ? '\u2705' :
         msg.type === 'error'   ? '\u274c' :
         msg.type === 'warning' ? '\u26a0\ufe0f' : '\u2139\ufe0f'}
      </span>
      <span className="toast-text">{msg.text}</span>
      <button
        className="toast-close"
        onClick={onClose}
        aria-label="Close notification"
      >
        <span aria-hidden="true">\u2715</span>
      </button>
    </div>
  );
}

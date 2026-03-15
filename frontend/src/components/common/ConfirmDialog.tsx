// =============================================================================
// ConfirmDialog — modal confirm used for all destructive actions
// Usage:
//   const [confirm, setConfirm] = useState<ConfirmState | null>(null);
//   <ConfirmDialog
//     open={!!confirm}
//     title="Delete Record"
//     message={`Delete SDR/2026-27/00001?`}
//     onConfirm={() => { doDelete(); setConfirm(null); }}
//     onCancel={() => setConfirm(null)}
//   />
// =============================================================================
import React, { useEffect, useRef } from 'react';
import './ConfirmDialog.css';
import Btn from './Btn';

interface Props {
  open:      boolean;
  title:     string;
  message:   string;
  confirmLabel?: string;
  cancelLabel?:  string;
  danger?:   boolean;
  onConfirm: () => void;
  onCancel:  () => void;
}

export default function ConfirmDialog({
  open, title, message,
  confirmLabel = 'Confirm',
  cancelLabel  = 'Cancel',
  danger       = true,
  onConfirm, onCancel,
}: Props) {
  const cancelBtnRef = useRef<HTMLButtonElement>(null);

  useEffect(() => {
    if (open && cancelBtnRef.current) {
      cancelBtnRef.current.focus();
    }
  }, [open]);

  // Trap focus or at least close on escape
  useEffect(() => {
    if (!open) return;
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape') onCancel();
    };
    document.addEventListener('keydown', handleKeyDown);
    return () => document.removeEventListener('keydown', handleKeyDown);
  }, [open, onCancel]);

  if (!open) return null;

  return (
    <div
      className="dialog-overlay"
      onClick={onCancel}
      role="dialog"
      aria-modal="true"
      aria-labelledby="confirm-dialog-title"
      aria-describedby="confirm-dialog-desc"
    >
      <div className="dialog-box" onClick={e => e.stopPropagation()}>
        <div id="confirm-dialog-title" className="dialog-title">{title}</div>
        <div id="confirm-dialog-desc" className="dialog-message">{message}</div>
        <div className="dialog-actions">
          <Btn
            variant="secondary"
            size="sm"
            onClick={onCancel}
            ref={cancelBtnRef}
          >
            {cancelLabel}
          </Btn>
          <Btn
            variant={danger ? 'danger' : 'primary'}
            size="sm"
            onClick={onConfirm}
          >
            {confirmLabel}
          </Btn>
        </div>
      </div>
    </div>
  );
}

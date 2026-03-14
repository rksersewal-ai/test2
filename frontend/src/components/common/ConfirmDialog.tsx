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
import React from 'react';
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
  if (!open) return null;
  return (
    <div className="dialog-overlay" onClick={onCancel}>
      <div className="dialog-box" onClick={e => e.stopPropagation()}>
        <div className="dialog-title">{title}</div>
        <div className="dialog-message">{message}</div>
        <div className="dialog-actions">
          <Btn variant="secondary" size="sm" onClick={onCancel}>{cancelLabel}</Btn>
          <Btn variant={danger ? 'danger' : 'primary'} size="sm" onClick={onConfirm}>
            {confirmLabel}
          </Btn>
        </div>
      </div>
    </div>
  );
}

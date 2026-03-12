import { ReactNode, useEffect } from 'react';

interface ModalProps {
  open:       boolean;
  onClose:    () => void;
  title:      string;
  children:   ReactNode;
  footer?:    ReactNode;
  size?:      'sm' | 'md' | 'lg' | 'xl';
}

export function Modal({ open, onClose, title, children, footer, size = 'md' }: ModalProps) {
  useEffect(() => {
    if (!open) return;
    const onKey = (e: KeyboardEvent) => { if (e.key === 'Escape') onClose(); };
    document.addEventListener('keydown', onKey);
    return () => document.removeEventListener('keydown', onKey);
  }, [open, onClose]);

  if (!open) return null;

  const sizeClass = size === 'lg' ? 'modal-lg' : size === 'xl' ? 'modal-xl' : '';

  return (
    <div className="modal-overlay" onClick={onClose} role="dialog" aria-modal aria-labelledby="modal-title">
      <div className={`modal ${sizeClass}`} onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h3 id="modal-title">{title}</h3>
          <button className="btn-ghost-icon" onClick={onClose} aria-label="Close modal" style={{ color: 'var(--c-text-secondary)' }}>\u00D7</button>
        </div>
        <div className="modal-body">{children}</div>
        {footer && <div className="modal-footer">{footer}</div>}
      </div>
    </div>
  );
}

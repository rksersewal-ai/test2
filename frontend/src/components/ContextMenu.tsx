import React, { useEffect, useRef } from 'react';
import styles from './ContextMenu.module.css';

export interface ContextMenuAction {
  label: string;
  icon?: string;
  onClick: () => void;
  disabled?: boolean;
  danger?: boolean;
  divider?: boolean;
}

export interface ContextMenuProps {
  x: number;
  y: number;
  visible: boolean;
  actions: ContextMenuAction[];
  onClose: () => void;
  title?: string;
}

export default function ContextMenu({ x, y, visible, actions, onClose, title }: ContextMenuProps) {
  const menuRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!visible) return;
    const handleClickOutside = (e: MouseEvent) => {
      if (menuRef.current && !menuRef.current.contains(e.target as Node)) {
        onClose();
      }
    };
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape') onClose();
    };
    document.addEventListener('mousedown', handleClickOutside);
    document.addEventListener('keydown', handleKeyDown);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
      document.removeEventListener('keydown', handleKeyDown);
    };
  }, [visible, onClose]);

  // Adjust position to avoid overflow
  const adjustedX = typeof window !== 'undefined' ? Math.min(x, window.innerWidth - 200) : x;
  const adjustedY = typeof window !== 'undefined' ? Math.min(y, window.innerHeight - 300) : y;

  if (!visible) return null;

  return (
    <div
      ref={menuRef}
      className={styles.contextMenu}
      style={{ left: adjustedX, top: adjustedY }}
      role="menu"
      aria-label="Context menu"
    >
      {title && <div className={styles.menuTitle}>{title}</div>}
      {actions.map((action, idx) =>
        action.divider ? (
          <div key={`divider-${idx}`} className={styles.divider} />
        ) : (
          <button
            key={idx}
            className={`${styles.menuItem} ${action.danger ? styles.danger : ''} ${action.disabled ? styles.disabled : ''}`}
            onClick={() => {
              if (!action.disabled) {
                action.onClick();
                onClose();
              }
            }}
            disabled={action.disabled}
            role="menuitem"
          >
            {action.icon && <span className={styles.icon}>{action.icon}</span>}
            <span>{action.label}</span>
          </button>
        )
      )}
    </div>
  );
}

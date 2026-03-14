// =============================================================================
// Reusable Button — use everywhere instead of raw <button>
// =============================================================================
import React from 'react';
import './Btn.css';

export type BtnVariant = 'primary' | 'secondary' | 'danger' | 'ghost' | 'gold';
export type BtnSize    = 'sm' | 'md' | 'lg';

interface BtnProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: BtnVariant;
  size?:    BtnSize;
  loading?: boolean;
  icon?:    React.ReactNode;
}

export default function Btn({
  variant = 'primary',
  size    = 'md',
  loading = false,
  icon,
  children,
  disabled,
  className = '',
  ...rest
}: BtnProps) {
  return (
    <button
      className={`btn btn-${variant} btn-${size} ${className}`.trim()}
      disabled={disabled || loading}
      {...rest}
    >
      {loading ? <span className="btn-spinner" /> : icon && <span className="btn-icon">{icon}</span>}
      {children && <span>{children}</span>}
    </button>
  );
}

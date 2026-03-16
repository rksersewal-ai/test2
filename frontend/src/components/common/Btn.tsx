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
  'aria-label': ariaLabel,
  ...rest
}: BtnProps) {
  // Warn if an icon-only button is missing an aria-label (development only)
  if (process.env.NODE_ENV !== 'production' && icon && !children && !ariaLabel && !rest.title) {
    console.warn('Btn component: Icon-only button is missing an aria-label or title for accessibility.');
  }

  return (
    <button
      className={`btn btn-${variant} btn-${size} ${className}`.trim()}
      disabled={disabled || loading}
      aria-label={ariaLabel}
      aria-busy={loading ? 'true' : undefined}
      {...rest}
    >
      {loading ? (
        <span className="btn-spinner" aria-hidden="true" />
      ) : icon ? (
        <span className="btn-icon" aria-hidden="true">{icon}</span>
      ) : null}
      {children && <span>{children}</span>}
    </button>
  );
}

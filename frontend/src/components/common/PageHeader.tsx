// =============================================================================
// FILE: frontend/src/components/common/PageHeader.tsx
// Supports: title, subtitle, back() callback, children (action buttons)
// =============================================================================
import React from 'react';
import './PageHeader.css';

interface Props {
  title: string;
  subtitle?: string;
  back?: () => void;
  children?: React.ReactNode;
}

export default function PageHeader({ title, subtitle, back, children }: Props) {
  return (
    <div className="ph-wrap">
      <div className="ph-left">
        {back && (
          <button
            className="ph-back"
            onClick={back}
            aria-label="Go back"
          >
            <span aria-hidden="true">←</span> Back
          </button>
        )}
        <div>
          <h1 className="ph-title">{title}</h1>
          {subtitle && <p className="ph-sub">{subtitle}</p>}
        </div>
      </div>
      {children && <div className="ph-actions">{children}</div>}
    </div>
  );
}

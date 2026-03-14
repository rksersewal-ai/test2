// =============================================================================
// PageHeader — standard top bar used on every list/detail page
// Usage:
//   <PageHeader title="Documents" subtitle="All controlled drawings">
//     <Btn onClick={...}>+ New</Btn>
//     <Btn variant="secondary" onClick={...}>Export</Btn>
//   </PageHeader>
// =============================================================================
import React from 'react';
import './PageHeader.css';

interface Props {
  title:     string;
  subtitle?: string;
  back?:     () => void;    // show ← Back button if provided
  children?: React.ReactNode; // action buttons injected here
}

export default function PageHeader({ title, subtitle, back, children }: Props) {
  return (
    <div className="page-header">
      <div className="page-header-left">
        {back && (
          <button className="back-btn" onClick={back} title="Go back">
            ← Back
          </button>
        )}
        <div>
          <h2 className="page-title">{title}</h2>
          {subtitle && <p className="page-subtitle">{subtitle}</p>}
        </div>
      </div>
      {children && <div className="page-header-actions">{children}</div>}
    </div>
  );
}

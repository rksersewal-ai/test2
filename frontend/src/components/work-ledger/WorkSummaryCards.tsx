// =============================================================================
// FILE: frontend/src/components/work-ledger/WorkSummaryCards.tsx
// PURPOSE: Monthly dashboard summary widget cards
// =============================================================================
import React from 'react';
import type { KpiRow } from '../../types/workLedger';

interface Props {
  month: string;
  total: number;
  byCategory: KpiRow[];
}

export const WorkSummaryCards: React.FC<Props> = ({ month, total, byCategory }) => (
  <div className="wl-summary-cards">
    <div className="wl-card wl-card--total">
      <span className="wl-card__value">{total}</span>
      <span className="wl-card__label">Total This Month ({month})</span>
    </div>
    {byCategory.map((row) => (
      <div key={row.work_category_code} className="wl-card">
        <span className="wl-card__value">{row.work_count}</span>
        <span className="wl-card__label">{row.work_category_label}</span>
      </div>
    ))}
  </div>
);

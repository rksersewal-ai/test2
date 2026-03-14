// =============================================================================
// FILE: frontend/src/components/work-ledger/WorkLedgerFilters.tsx
// PURPOSE: Report filter bar for Work Activity Report
// =============================================================================
import React, { useState } from 'react';
import type { WorkCategory, ActivityReportFilters } from '../../types/workLedger';

interface Props {
  categories: WorkCategory[];
  onApply: (filters: ActivityReportFilters) => void;
}

export const WorkLedgerFilters: React.FC<Props> = ({ categories, onApply }) => {
  const [filters, setFilters] = useState<ActivityReportFilters>({});

  const set = (key: keyof ActivityReportFilters, value: string) =>
    setFilters((prev) => ({ ...prev, [key]: value || undefined }));

  return (
    <div className="wl-filters">
      <div className="wl-filters__row">
        <label>From Date
          <input type="date" onChange={(e) => set('from_date', e.target.value)} />
        </label>
        <label>To Date
          <input type="date" onChange={(e) => set('to_date', e.target.value)} />
        </label>
        <label>Section
          <select onChange={(e) => set('section', e.target.value)}>
            <option value="">All</option>
            <option value="Mechanical">Mechanical</option>
            <option value="Electrical">Electrical</option>
            <option value="General">General</option>
          </select>
        </label>
        <label>Category
          <select onChange={(e) => set('category', e.target.value)}>
            <option value="">All</option>
            {categories.map((c) => (
              <option key={c.code} value={c.code}>{c.label}</option>
            ))}
          </select>
        </label>
        <label>PL Number
          <input type="text" onChange={(e) => set('pl_number', e.target.value)} />
        </label>
        <label>Status
          <select onChange={(e) => set('status', e.target.value)}>
            <option value="">All</option>
            <option value="Open">Open</option>
            <option value="Closed">Closed</option>
            <option value="Pending">Pending</option>
          </select>
        </label>
      </div>
      <button className="wl-btn wl-btn--primary" onClick={() => onApply(filters)}>
        Generate Report
      </button>
    </div>
  );
};

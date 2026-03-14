// =============================================================================
// FILE: frontend/src/pages/work-ledger/WorkActivityReportPage.tsx
// PURPOSE: Filtered tabular work activity report with export
// =============================================================================
import React, { useEffect, useState } from 'react';
import { WorkLedgerFilters } from '../../components/work-ledger/WorkLedgerFilters';
import { workLedgerApi } from '../../services/workLedgerApi';
import type { ActivityReportFilters, ActivityReportRow, WorkCategory } from '../../types/workLedger';

export const WorkActivityReportPage: React.FC = () => {
  const [categories, setCategories] = useState<WorkCategory[]>([]);
  const [rows, setRows] = useState<ActivityReportRow[]>([]);
  const [loading, setLoading] = useState(false);
  const [activeFilters, setActiveFilters] = useState<ActivityReportFilters>({});

  useEffect(() => {
    workLedgerApi.getCategories().then(setCategories);
  }, []);

  const handleApply = async (filters: ActivityReportFilters) => {
    setActiveFilters(filters);
    setLoading(true);
    try {
      const data = await workLedgerApi.getActivityReport(filters);
      setRows(data);
    } finally {
      setLoading(false);
    }
  };

  const handleExport = (fmt: 'csv' | 'xlsx' | 'pdf') => {
    const url = workLedgerApi.getExportUrl(activeFilters, fmt);
    window.open(url, '_blank');
  };

  return (
    <div className="wl-report-page">
      <h2>Work Activity Report</h2>
      <WorkLedgerFilters categories={categories} onApply={handleApply} />

      <div className="wl-report-actions">
        <button className="wl-btn" onClick={() => handleExport('csv')}>Export CSV</button>
        <button className="wl-btn" onClick={() => handleExport('xlsx')}>Export Excel</button>
        <button className="wl-btn" onClick={() => handleExport('pdf')}>Export PDF</button>
        <button className="wl-btn" onClick={() => window.print()}>Print</button>
      </div>

      {loading ? (
        <p className="wl-loading">Loading report...</p>
      ) : (
        <div className="wl-table-wrapper">
          <table className="wl-table">
            <thead>
              <tr>
                <th>Date</th>
                <th>Work Code</th>
                <th>Section</th>
                <th>Category</th>
                <th>PL Number</th>
                <th>Drawing</th>
                <th>Tender No</th>
                <th>Status</th>
                <th>Remarks</th>
              </tr>
            </thead>
            <tbody>
              {rows.length === 0 ? (
                <tr><td colSpan={9} className="wl-empty">No records found. Apply filters and generate report.</td></tr>
              ) : (
                rows.map((r) => (
                  <tr key={r.work_id}>
                    <td>{r.received_date}</td>
                    <td>{r.work_code}</td>
                    <td>{r.section}</td>
                    <td>{r.work_category_label}</td>
                    <td>{r.pl_number ?? '-'}</td>
                    <td>{r.drawing_number ?? '-'}</td>
                    <td>{r.tender_number ?? '-'}</td>
                    <td><span className={`wl-badge wl-badge--${r.status.toLowerCase()}`}>{r.status}</span></td>
                    <td>{r.remarks ?? '-'}</td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
};

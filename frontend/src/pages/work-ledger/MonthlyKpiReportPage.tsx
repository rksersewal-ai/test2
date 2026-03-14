// =============================================================================
// FILE: frontend/src/pages/work-ledger/MonthlyKpiReportPage.tsx
// PURPOSE: Monthly KPI Summary report page
// =============================================================================
import React, { useEffect, useState } from 'react';
import { WorkSummaryCards } from '../../components/work-ledger/WorkSummaryCards';
import { workLedgerApi } from '../../services/workLedgerApi';
import type { KpiRow } from '../../types/workLedger';

export const MonthlyKpiReportPage: React.FC = () => {
  const today = new Date();
  const [year, setYear] = useState(today.getFullYear());
  const [month, setMonth] = useState(today.getMonth() + 1);
  const [section, setSection] = useState('');
  const [summary, setSummary] = useState<KpiRow[]>([]);
  const [loading, setLoading] = useState(false);

  const fetchKpi = async () => {
    setLoading(true);
    try {
      const data = await workLedgerApi.getMonthlyKpi(year, month, section || undefined);
      setSummary(data.summary);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchKpi(); }, []); // eslint-disable-line

  const total = summary.reduce((acc, r) => acc + r.work_count, 0);

  return (
    <div className="wl-kpi-page">
      <h2>Monthly Work Summary – KPI Report</h2>

      <div className="wl-kpi-controls">
        <label>Year
          <input type="number" value={year} min={2020} max={2099}
            onChange={(e) => setYear(Number(e.target.value))} />
        </label>
        <label>Month
          <input type="number" value={month} min={1} max={12}
            onChange={(e) => setMonth(Number(e.target.value))} />
        </label>
        <label>Section
          <select value={section} onChange={(e) => setSection(e.target.value)}>
            <option value="">All Sections</option>
            <option value="Mechanical">Mechanical</option>
            <option value="Electrical">Electrical</option>
            <option value="General">General</option>
          </select>
        </label>
        <button className="wl-btn wl-btn--primary" onClick={fetchKpi}>Load</button>
        <button className="wl-btn" onClick={() => window.print()}>Print Report</button>
      </div>

      {loading ? (
        <p className="wl-loading">Loading KPI data...</p>
      ) : (
        <>
          <WorkSummaryCards
            month={`${year}-${String(month).padStart(2, '0')}`}
            total={total}
            byCategory={summary}
          />
          <div className="wl-table-wrapper">
            <h3>MONTHLY WORK SUMMARY – {year}-{String(month).padStart(2, '0')}</h3>
            <table className="wl-table wl-table--kpi">
              <thead>
                <tr>
                  <th>Activity</th>
                  <th>Count</th>
                </tr>
              </thead>
              <tbody>
                {summary.map((r) => (
                  <tr key={r.work_category_code}>
                    <td>{r.work_category_label}</td>
                    <td className="wl-count">{r.work_count}</td>
                  </tr>
                ))}
                <tr className="wl-total-row">
                  <td><strong>Total</strong></td>
                  <td className="wl-count"><strong>{total}</strong></td>
                </tr>
              </tbody>
            </table>
          </div>
        </>
      )}
    </div>
  );
};

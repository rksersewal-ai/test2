import React, { useEffect, useState } from 'react';
import { workLedgerService } from '../../services/workLedgerService';
import type { KpiRow, WorkLedgerSectionOption } from '../../types/workLedger';

export const MonthlyKpiReportPage: React.FC = () => {
  const today = new Date();
  const [year, setYear] = useState(today.getFullYear());
  const [month, setMonth] = useState(today.getMonth() + 1);
  const [section, setSection] = useState('');
  const [sections, setSections] = useState<WorkLedgerSectionOption[]>([]);
  const [summary, setSummary] = useState<KpiRow[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const fetchKpi = async () => {
    setLoading(true);
    setError('');
    try {
      const data = await workLedgerService.getMonthlyKpi(year, month, section || undefined);
      setSummary(data.summary);
    } catch {
      setError('Failed to load KPI data.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    void workLedgerService.getSections().then(setSections).catch(() => {});
    void workLedgerService.getMonthlyKpi(year, month).then(data => {
      setSummary(data.summary);
    }).catch(() => {
      setError('Failed to load KPI data.');
    });
  }, []);

  const total = summary.reduce((accumulator, row) => accumulator + row.work_count, 0);
  const monthLabel = `${year}-${String(month).padStart(2, '0')}`;

  const btnStyle: React.CSSProperties = {
    padding: '7px 16px',
    background: '#1e2332',
    border: '1px solid #2d3555',
    color: '#d1d5db',
    borderRadius: 6,
    fontSize: 13,
    cursor: 'pointer',
  };
  const primaryBtn: React.CSSProperties = {
    ...btnStyle,
    background: 'linear-gradient(135deg,#4b6cb7,#182848)',
    border: 'none',
    color: '#fff',
    fontWeight: 600,
  };

  return (
    <div style={{ padding: 24 }}>
      <h2 style={{ color: '#e2e8f0', fontSize: 20, fontWeight: 700, marginBottom: 20 }}>
        Monthly Work Summary - KPI Report
      </h2>

      {error && (
        <div
          style={{
            background: '#7f1d1d',
            color: '#fecaca',
            padding: '10px 16px',
            borderRadius: 8,
            marginBottom: 16,
            fontSize: 13,
          }}
        >
          {error}
        </div>
      )}

      <div style={{ display: 'flex', gap: 12, flexWrap: 'wrap', marginBottom: 20, alignItems: 'flex-end' }}>
        <label style={{ color: '#94a3b8', fontSize: 12, fontWeight: 600 }}>
          Year
          <input
            type="number"
            value={year}
            min={2020}
            max={2099}
            onChange={event => setYear(Number(event.target.value))}
            style={{
              display: 'block',
              marginTop: 4,
              width: 90,
              padding: '6px 10px',
              background: '#1e2332',
              border: '1px solid #2d3555',
              color: '#d1d5db',
              borderRadius: 6,
              fontSize: 13,
            }}
          />
        </label>

        <label style={{ color: '#94a3b8', fontSize: 12, fontWeight: 600 }}>
          Month
          <input
            type="number"
            value={month}
            min={1}
            max={12}
            onChange={event => setMonth(Number(event.target.value))}
            style={{
              display: 'block',
              marginTop: 4,
              width: 70,
              padding: '6px 10px',
              background: '#1e2332',
              border: '1px solid #2d3555',
              color: '#d1d5db',
              borderRadius: 6,
              fontSize: 13,
            }}
          />
        </label>

        <label style={{ color: '#94a3b8', fontSize: 12, fontWeight: 600 }}>
          Section
          <select
            value={section}
            onChange={event => setSection(event.target.value)}
            style={{
              display: 'block',
              marginTop: 4,
              padding: '6px 10px',
              background: '#1e2332',
              border: '1px solid #2d3555',
              color: '#d1d5db',
              borderRadius: 6,
              fontSize: 13,
            }}
          >
            <option value="">All Sections</option>
            {sections
              .slice()
              .sort((left, right) => left.name.localeCompare(right.name))
              .map(nextSection => (
                <option key={nextSection.code} value={nextSection.name}>
                  {nextSection.name}
                </option>
              ))}
          </select>
        </label>

        <button style={primaryBtn} onClick={() => void fetchKpi()}>Load</button>
        <button style={btnStyle} onClick={() => window.print()}>Print</button>
      </div>

      {loading ? (
        <p style={{ color: '#94a3b8', fontSize: 13 }}>Loading KPI data...</p>
      ) : (
        <div style={{ background: '#151b2e', border: '1px solid #2d3555', borderRadius: 10, overflow: 'hidden' }}>
          <div
            style={{
              padding: '12px 20px',
              background: '#1a2238',
              borderBottom: '1px solid #2d3555',
              color: '#4b6cb7',
              fontWeight: 700,
              fontSize: 13,
              letterSpacing: '0.06em',
            }}
          >
            MONTHLY WORK SUMMARY - {monthLabel}
          </div>

          <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: 13 }}>
            <thead>
              <tr style={{ background: '#1e2b45' }}>
                <th style={{ padding: '10px 20px', textAlign: 'left', color: '#94a3b8', fontWeight: 600 }}>
                  Activity
                </th>
                <th style={{ padding: '10px 20px', textAlign: 'right', color: '#94a3b8', fontWeight: 600 }}>
                  Count
                </th>
              </tr>
            </thead>
            <tbody>
              {summary.length === 0 ? (
                <tr>
                  <td colSpan={2} style={{ padding: '20px', textAlign: 'center', color: '#4b5563' }}>
                    No data for this period.
                  </td>
                </tr>
              ) : (
                summary.map(row => (
                  <tr key={row.work_category_code} style={{ borderBottom: '1px solid #1e2a3e' }}>
                    <td style={{ padding: '10px 20px', color: '#d1d5db' }}>{row.work_category_label}</td>
                    <td style={{ padding: '10px 20px', textAlign: 'right', color: '#60a5fa', fontWeight: 600 }}>
                      {row.work_count}
                    </td>
                  </tr>
                ))
              )}
              {summary.length > 0 && (
                <tr style={{ background: '#1a2238', borderTop: '2px solid #2d3555' }}>
                  <td style={{ padding: '10px 20px', color: '#e2e8f0', fontWeight: 700 }}>Total</td>
                  <td
                    style={{
                      padding: '10px 20px',
                      textAlign: 'right',
                      color: '#34d399',
                      fontWeight: 700,
                      fontSize: 15,
                    }}
                  >
                    {total}
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
};

export default MonthlyKpiReportPage;

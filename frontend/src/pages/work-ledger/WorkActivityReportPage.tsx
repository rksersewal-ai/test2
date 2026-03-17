import React, { useEffect, useState } from 'react';
import { workLedgerService } from '../../services/workLedgerService';
import type { ActivityReportFilters, ActivityReportRow, WorkCategory } from '../../types/workLedger';

export const WorkActivityReportPage: React.FC = () => {
  const [categories, setCategories] = useState<WorkCategory[]>([]);
  const [rows, setRows] = useState<ActivityReportRow[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [filters, setFilters] = useState<ActivityReportFilters>({});

  useEffect(() => {
    workLedgerService.getCategories().then(setCategories).catch(() => {});
  }, []);

  const setFilter = (key: keyof ActivityReportFilters, value: string | number | undefined) => {
    setFilters(current => ({ ...current, [key]: value || undefined }));
  };

  const handleApply = async () => {
    setLoading(true);
    setError('');
    try {
      const data = await workLedgerService.getActivityReport(filters);
      setRows(data);
    } catch {
      setError('Failed to load report data.');
    } finally {
      setLoading(false);
    }
  };

  const handleExport = () => {
    const url = workLedgerService.getExportUrl(filters, 'csv');
    window.open(url, '_blank');
  };

  const inputStyle: React.CSSProperties = {
    padding: '6px 10px',
    background: '#1e2332',
    border: '1px solid #2d3555',
    color: '#d1d5db',
    borderRadius: 6,
    fontSize: 13,
  };
  const btnStyle: React.CSSProperties = {
    padding: '7px 14px',
    background: '#1e2332',
    border: '1px solid #2d3555',
    color: '#d1d5db',
    borderRadius: 6,
    fontSize: 13,
    cursor: 'pointer',
  };

  const STATUS_COLORS: Record<string, string> = {
    DRAFT: '#fbbf24',
    SUBMITTED: '#60a5fa',
    VERIFIED: '#34d399',
    APPROVED: '#22c55e',
    RETURNED: '#f97316',
  };

  return (
    <div style={{ padding: 24 }}>
      <h2 style={{ color: '#e2e8f0', fontSize: 20, fontWeight: 700, marginBottom: 20 }}>
        Work Activity Report
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

      <div
        style={{
          display: 'flex',
          gap: 12,
          flexWrap: 'wrap',
          marginBottom: 16,
          alignItems: 'flex-end',
          background: '#151b2e',
          padding: '16px 20px',
          borderRadius: 10,
          border: '1px solid #2d3555',
        }}
      >
        {([
          ['from_date', 'From Date', 'date'],
          ['to_date', 'To Date', 'date'],
          ['pl_number', 'PL Number', 'text'],
        ] as [keyof ActivityReportFilters, string, string][]).map(([key, label, type]) => (
          <label key={key} style={{ color: '#94a3b8', fontSize: 12, fontWeight: 600 }}>
            {label}
            <input
              type={type}
              style={{ display: 'block', marginTop: 4, ...inputStyle }}
              value={(filters[key] as string) ?? ''}
              onChange={event => setFilter(key, event.target.value)}
            />
          </label>
        ))}

        <label style={{ color: '#94a3b8', fontSize: 12, fontWeight: 600 }}>
          Section
          <select
            style={{ display: 'block', marginTop: 4, ...inputStyle }}
            value={filters.section ?? ''}
            onChange={event => setFilter('section', event.target.value)}
          >
            <option value="">All</option>
            <option value="Mechanical">Mechanical</option>
            <option value="Electrical">Electrical</option>
            <option value="General">General</option>
          </select>
        </label>

        <label style={{ color: '#94a3b8', fontSize: 12, fontWeight: 600 }}>
          Category
          <select
            style={{ display: 'block', marginTop: 4, ...inputStyle }}
            value={filters.category ?? ''}
            onChange={event => setFilter('category', event.target.value)}
          >
            <option value="">All</option>
            {categories.map(category => (
              <option key={category.code} value={category.code}>
                {category.label}
              </option>
            ))}
          </select>
        </label>

        <label style={{ color: '#94a3b8', fontSize: 12, fontWeight: 600 }}>
          Status
          <select
            style={{ display: 'block', marginTop: 4, ...inputStyle }}
            value={filters.status ?? ''}
            onChange={event => setFilter('status', event.target.value)}
          >
            <option value="">All</option>
            <option value="DRAFT">Draft</option>
            <option value="SUBMITTED">Submitted</option>
            <option value="VERIFIED">Verified</option>
            <option value="APPROVED">Approved</option>
            <option value="RETURNED">Returned</option>
          </select>
        </label>

        <button
          style={{
            ...btnStyle,
            background: 'linear-gradient(135deg,#4b6cb7,#182848)',
            border: 'none',
            color: '#fff',
            fontWeight: 600,
            alignSelf: 'flex-end',
          }}
          onClick={handleApply}
        >
          Generate Report
        </button>
      </div>

      <div style={{ display: 'flex', gap: 8, marginBottom: 16 }}>
        <button style={btnStyle} onClick={handleExport}>Export CSV</button>
        <button style={btnStyle} onClick={() => window.print()}>Print</button>
      </div>

      {loading ? (
        <p style={{ color: '#94a3b8', fontSize: 13 }}>Loading report...</p>
      ) : (
        <div
          style={{
            overflowX: 'auto',
            background: '#151b2e',
            borderRadius: 10,
            border: '1px solid #2d3555',
          }}
        >
          <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: 13 }}>
            <thead>
              <tr style={{ background: '#1e2b45' }}>
                {['Date', 'Work Code', 'Section', 'Category', 'PL No.', 'Drawing', 'Tender No.', 'Status', 'Remarks'].map(
                  header => (
                    <th
                      key={header}
                      style={{
                        padding: '10px 14px',
                        textAlign: 'left',
                        color: '#94a3b8',
                        fontWeight: 600,
                        whiteSpace: 'nowrap',
                      }}
                    >
                      {header}
                    </th>
                  )
                )}
              </tr>
            </thead>
            <tbody>
              {rows.length === 0 ? (
                <tr>
                  <td colSpan={9} style={{ padding: 24, textAlign: 'center', color: '#4b5563' }}>
                    Apply filters and click Generate Report.
                  </td>
                </tr>
              ) : (
                rows.map(row => (
                  <tr key={row.work_id} style={{ borderBottom: '1px solid #1e2a3e' }}>
                    <td style={{ padding: '9px 14px', color: '#d1d5db' }}>{row.received_date}</td>
                    <td style={{ padding: '9px 14px', color: '#60a5fa', fontFamily: 'monospace' }}>{row.work_code}</td>
                    <td style={{ padding: '9px 14px', color: '#d1d5db' }}>{row.section}</td>
                    <td style={{ padding: '9px 14px', color: '#d1d5db' }}>{row.work_category_label}</td>
                    <td style={{ padding: '9px 14px', color: '#d1d5db', fontFamily: 'monospace' }}>{row.pl_number ?? '-'}</td>
                    <td style={{ padding: '9px 14px', color: '#d1d5db', fontFamily: 'monospace' }}>{row.drawing_number ?? '-'}</td>
                    <td style={{ padding: '9px 14px', color: '#d1d5db' }}>{row.tender_number ?? '-'}</td>
                    <td style={{ padding: '9px 14px' }}>
                      <span
                        style={{
                          padding: '2px 8px',
                          borderRadius: 4,
                          fontSize: 11,
                          fontWeight: 700,
                          background: STATUS_COLORS[row.status] ? `${STATUS_COLORS[row.status]}22` : '#1e2332',
                          color: STATUS_COLORS[row.status] ?? '#d1d5db',
                        }}
                      >
                        {row.status.replace('_', ' ')}
                      </span>
                    </td>
                    <td style={{ padding: '9px 14px', color: '#94a3b8' }}>{row.remarks ?? '-'}</td>
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

export default WorkActivityReportPage;

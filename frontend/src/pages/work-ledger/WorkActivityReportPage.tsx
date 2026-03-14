// =============================================================================
// FILE: frontend/src/pages/work-ledger/WorkActivityReportPage.tsx
// FIX: Added `export default`. Switched to workLedgerService (direct, no alias).
//      getCategories / getActivityReport / getExportUrl now exist in service.
// =============================================================================
import React, { useEffect, useState } from 'react';
import { workLedgerService } from '../../services/workLedgerService';
import type { ActivityReportFilters, ActivityReportRow, WorkCategory } from '../../types/workLedger';

export const WorkActivityReportPage: React.FC = () => {
  const [categories, setCategories] = useState<WorkCategory[]>([]);
  const [rows,       setRows]       = useState<ActivityReportRow[]>([]);
  const [loading,    setLoading]    = useState(false);
  const [error,      setError]      = useState('');
  const [filters,    setFilters]    = useState<ActivityReportFilters>({});

  useEffect(() => {
    workLedgerService.getCategories().then(setCategories).catch(() => {});
  }, []);

  const sf = (k: keyof ActivityReportFilters, v: any) =>
    setFilters(f => ({ ...f, [k]: v || undefined }));

  const handleApply = async () => {
    setLoading(true); setError('');
    try {
      const data = await workLedgerService.getActivityReport(filters);
      setRows(data);
    } catch { setError('Failed to load report data.'); }
    finally { setLoading(false); }
  };

  const handleExport = (fmt: 'csv' | 'xlsx' | 'pdf') => {
    const url = workLedgerService.getExportUrl(filters, fmt);
    window.open(url, '_blank');
  };

  const inputStyle: React.CSSProperties = {
    padding: '6px 10px', background: '#1e2332',
    border: '1px solid #2d3555', color: '#d1d5db',
    borderRadius: 6, fontSize: 13,
  };
  const btnStyle: React.CSSProperties = {
    padding: '7px 14px', background: '#1e2332',
    border: '1px solid #2d3555', color: '#d1d5db',
    borderRadius: 6, fontSize: 13, cursor: 'pointer',
  };

  const STATUS_COLORS: Record<string, string> = {
    Open: '#fbbf24', Closed: '#34d399', Pending: '#60a5fa',
  };

  return (
    <div style={{ padding: 24 }}>
      <h2 style={{ color: '#e2e8f0', fontSize: 20, fontWeight: 700, marginBottom: 20 }}>
        📋 Work Activity Report
      </h2>

      {error && (
        <div style={{ background: '#7f1d1d', color: '#fecaca', padding: '10px 16px', borderRadius: 8, marginBottom: 16, fontSize: 13 }}>
          ❌ {error}
        </div>
      )}

      {/* Filters */}
      <div style={{ display: 'flex', gap: 12, flexWrap: 'wrap', marginBottom: 16, alignItems: 'flex-end',
        background: '#151b2e', padding: '16px 20px', borderRadius: 10, border: '1px solid #2d3555' }}>
        {[
          ['from_date', 'From Date', 'date'],
          ['to_date',   'To Date',   'date'],
          ['pl_number', 'PL Number', 'text'],
        ].map(([k, label, type]) => (
          <label key={k} style={{ color: '#94a3b8', fontSize: 12, fontWeight: 600 }}>
            {label}
            <input type={type} style={{ display: 'block', marginTop: 4, ...inputStyle }}
              value={(filters[k as keyof ActivityReportFilters] as string) ?? ''}
              onChange={e => sf(k as keyof ActivityReportFilters, e.target.value)} />
          </label>
        ))}
        <label style={{ color: '#94a3b8', fontSize: 12, fontWeight: 600 }}>
          Section
          <select style={{ display: 'block', marginTop: 4, ...inputStyle }}
            value={filters.section ?? ''} onChange={e => sf('section', e.target.value)}>
            <option value="">All</option>
            <option value="Mechanical">Mechanical</option>
            <option value="Electrical">Electrical</option>
            <option value="General">General</option>
          </select>
        </label>
        <label style={{ color: '#94a3b8', fontSize: 12, fontWeight: 600 }}>
          Category
          <select style={{ display: 'block', marginTop: 4, ...inputStyle }}
            value={filters.category ?? ''} onChange={e => sf('category', e.target.value)}>
            <option value="">All</option>
            {categories.map(c => <option key={c.code} value={c.code}>{c.label}</option>)}
          </select>
        </label>
        <label style={{ color: '#94a3b8', fontSize: 12, fontWeight: 600 }}>
          Status
          <select style={{ display: 'block', marginTop: 4, ...inputStyle }}
            value={filters.status ?? ''} onChange={e => sf('status', e.target.value)}>
            <option value="">All</option>
            <option value="Open">Open</option>
            <option value="Pending">Pending</option>
            <option value="Closed">Closed</option>
          </select>
        </label>
        <button
          style={{ ...btnStyle, background: 'linear-gradient(135deg,#4b6cb7,#182848)', border: 'none', color: '#fff', fontWeight: 600, alignSelf: 'flex-end' }}
          onClick={handleApply}>
          🔍 Generate Report
        </button>
      </div>

      {/* Export buttons */}
      <div style={{ display: 'flex', gap: 8, marginBottom: 16 }}>
        <button style={btnStyle} onClick={() => handleExport('csv')}>⬇ CSV</button>
        <button style={btnStyle} onClick={() => handleExport('xlsx')}>⬇ Excel</button>
        <button style={btnStyle} onClick={() => handleExport('pdf')}>⬇ PDF</button>
        <button style={btnStyle} onClick={() => window.print()}>🖨️ Print</button>
      </div>

      {/* Table */}
      {loading ? (
        <p style={{ color: '#94a3b8', fontSize: 13 }}>Loading report…</p>
      ) : (
        <div style={{ overflowX: 'auto', background: '#151b2e', borderRadius: 10, border: '1px solid #2d3555' }}>
          <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: 13 }}>
            <thead>
              <tr style={{ background: '#1e2b45' }}>
                {['Date', 'Work Code', 'Section', 'Category', 'PL No.', 'Drawing', 'Tender No.', 'Status', 'Remarks']
                  .map(h => (
                    <th key={h} style={{ padding: '10px 14px', textAlign: 'left', color: '#94a3b8', fontWeight: 600, whiteSpace: 'nowrap' }}>{h}</th>
                  ))}
              </tr>
            </thead>
            <tbody>
              {rows.length === 0 ? (
                <tr><td colSpan={9} style={{ padding: 24, textAlign: 'center', color: '#4b5563' }}>Apply filters and click Generate Report.</td></tr>
              ) : (
                rows.map(r => (
                  <tr key={r.work_id} style={{ borderBottom: '1px solid #1e2a3e' }}>
                    <td style={{ padding: '9px 14px', color: '#d1d5db' }}>{r.received_date}</td>
                    <td style={{ padding: '9px 14px', color: '#60a5fa', fontFamily: 'monospace' }}>{r.work_code}</td>
                    <td style={{ padding: '9px 14px', color: '#d1d5db' }}>{r.section}</td>
                    <td style={{ padding: '9px 14px', color: '#d1d5db' }}>{r.work_category_label}</td>
                    <td style={{ padding: '9px 14px', color: '#d1d5db', fontFamily: 'monospace' }}>{r.pl_number ?? '—'}</td>
                    <td style={{ padding: '9px 14px', color: '#d1d5db', fontFamily: 'monospace' }}>{r.drawing_number ?? '—'}</td>
                    <td style={{ padding: '9px 14px', color: '#d1d5db' }}>{r.tender_number ?? '—'}</td>
                    <td style={{ padding: '9px 14px' }}>
                      <span style={{ padding: '2px 8px', borderRadius: 4, fontSize: 11, fontWeight: 700,
                        background: STATUS_COLORS[r.status] ? STATUS_COLORS[r.status] + '22' : '#1e2332',
                        color: STATUS_COLORS[r.status] ?? '#d1d5db' }}>
                        {r.status}
                      </span>
                    </td>
                    <td style={{ padding: '9px 14px', color: '#94a3b8' }}>{r.remarks ?? '—'}</td>
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

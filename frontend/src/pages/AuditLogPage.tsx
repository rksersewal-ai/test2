// =============================================================================
// FILE: frontend/src/pages/AuditLogPage.tsx  (Phase 4 — real API)
// Audit trail viewer: filter by user, action, model, date range
// =============================================================================
import React, { useState, useEffect, useCallback } from 'react';
import { PageHeader, Btn, SearchBar, Toast } from '../components/common';
import type { ToastMsg } from '../components/common';
import api from '../api/axios';
import './AuditLogPage.css';

const auditService = {
  list: (params?: Record<string,string>) =>
    api.get('/audit/logs/', { params }).then(r => r.data),
  export: (params?: Record<string,string>) =>
    api.get('/audit/logs/export/', { params, responseType: 'blob' }).then(r => r.data),
};

const ACTION_CLS: Record<string,string> = {
  CREATE: 'al-badge-create', UPDATE: 'al-badge-update',
  DELETE: 'al-badge-delete', VIEW:   'al-badge-view',
  APPROVE:'al-badge-approve',REJECT: 'al-badge-reject',
  LOGIN:  'al-badge-login',  LOGOUT: 'al-badge-logout',
  EXPORT: 'al-badge-view',
};

export default function AuditLogPage() {
  const [logs,    setLogs]    = useState<any[]>([]);
  const [total,   setTotal]   = useState(0);
  const [page,    setPage]    = useState(1);
  const [search,  setSearch]  = useState('');
  const [action,  setAction]  = useState('');
  const [model,   setModel]   = useState('');
  const [dateFrom,setDateFrom]= useState('');
  const [dateTo,  setDateTo]  = useState('');
  const [loading, setLoading] = useState(false);
  const [toast,   setToast]   = useState<ToastMsg|null>(null);
  const [expanded,setExpanded]= useState<number|null>(null);
  const PAGE_SIZE = 30;

  const buildParams = useCallback(() => {
    const p: Record<string,string> = { page: String(page), page_size: String(PAGE_SIZE) };
    if (search)   p.search      = search;
    if (action)   p.action      = action;
    if (model)    p.model       = model;
    if (dateFrom) p.date_from   = dateFrom;
    if (dateTo)   p.date_to     = dateTo;
    return p;
  }, [page, search, action, model, dateFrom, dateTo]);

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const data = await auditService.list(buildParams());
      setLogs(data.results ?? data ?? []);
      setTotal(data.count ?? data.total_count ?? 0);
    } catch { setToast({ type:'error', text:'Failed to load audit logs.' }); }
    finally  { setLoading(false); }
  }, [buildParams]);

  useEffect(() => { load(); }, [load]);

  const handleExport = async () => {
    try {
      const blob = await auditService.export(buildParams());
      const url  = URL.createObjectURL(blob);
      const a    = document.createElement('a');
      a.href     = url;
      a.download = `audit_log_${new Date().toISOString().slice(0,10)}.csv`;
      a.click();
      URL.revokeObjectURL(url);
      setToast({ type:'success', text:'Audit log exported.' });
    } catch { setToast({ type:'error', text:'Export failed.' }); }
  };

  const clearFilters = () => {
    setSearch(''); setAction(''); setModel('');
    setDateFrom(''); setDateTo(''); setPage(1);
  };

  const totalPages = Math.ceil(total / PAGE_SIZE);
  const hasFilters = search || action || model || dateFrom || dateTo;

  return (
    <div className="al-page">
      <PageHeader title="Audit Log" subtitle="All system actions — create, update, delete, approvals, logins">
        <Btn size="sm" variant="secondary" onClick={handleExport}>📥 Export CSV</Btn>
      </PageHeader>
      <Toast msg={toast} onClose={() => setToast(null)} />

      {/* Filter bar */}
      <div className="al-toolbar">
        <SearchBar value={search} onChange={v => { setSearch(v); setPage(1); }} placeholder="Search user, object, description…" width={260} />
        <select className="al-select" value={action} onChange={e => { setAction(e.target.value); setPage(1); }}>
          <option value="">All Actions</option>
          {['CREATE','UPDATE','DELETE','VIEW','APPROVE','REJECT','LOGIN','LOGOUT','EXPORT'].map(a =>
            <option key={a} value={a}>{a}</option>)}
        </select>
        <select className="al-select" value={model} onChange={e => { setModel(e.target.value); setPage(1); }}>
          <option value="">All Models</option>
          {['Document','PLMaster','WorkEntry','SDR','LocoConfig','ECN','User','OCRJob'].map(m =>
            <option key={m} value={m}>{m}</option>)}
        </select>
        <input type="date" className="al-date" value={dateFrom} onChange={e => { setDateFrom(e.target.value); setPage(1); }} title="Date from" />
        <input type="date" className="al-date" value={dateTo}   onChange={e => { setDateTo(e.target.value);   setPage(1); }} title="Date to" />
        <Btn size="sm" variant="ghost" onClick={load}>↺</Btn>
        {hasFilters && <Btn size="sm" variant="ghost" onClick={clearFilters}>✕ Clear</Btn>}
      </div>

      {/* Table */}
      <div className="al-table-wrap">
        <table className="al-table">
          <thead><tr>
            <th>#</th><th>Timestamp</th><th>User</th><th>Action</th>
            <th>Model</th><th>Object</th><th>IP Address</th><th>ℹ</th>
          </tr></thead>
          <tbody>
            {loading && <tr><td colSpan={8} className="al-center al-muted">Loading…</td></tr>}
            {!loading && logs.length===0 && <tr><td colSpan={8} className="al-center al-muted">No audit logs found.</td></tr>}
            {logs.map(log => (
              <React.Fragment key={log.id}>
                <tr
                  className={`al-row${expanded===log.id?' al-row--expanded':''}`}
                  onClick={() => setExpanded(x => x===log.id ? null : log.id)}
                >
                  <td className="al-mono al-muted">{log.id}</td>
                  <td className="al-muted" style={{fontSize:11,whiteSpace:'nowrap'}}>
                    {log.timestamp ? new Date(log.timestamp).toLocaleString('en-IN') : '—'}
                  </td>
                  <td className="al-user">{log.user_name ?? log.user ?? 'System'}</td>
                  <td><span className={`al-badge ${ACTION_CLS[log.action] ?? 'al-badge-view'}`}>{log.action}</span></td>
                  <td className="al-muted">{log.model ?? log.content_type ?? '—'}</td>
                  <td className="al-obj">{log.object_repr ?? log.object_id ?? '—'}</td>
                  <td className="al-mono al-muted">{log.ip_address ?? '—'}</td>
                  <td className="al-center al-muted" style={{fontSize:11}}>{log.changes ? '▼' : '—'}</td>
                </tr>
                {expanded===log.id && log.changes && (
                  <tr className="al-detail-row">
                    <td colSpan={8}>
                      <pre className="al-changes-pre">{typeof log.changes === 'string' ? log.changes : JSON.stringify(log.changes, null, 2)}</pre>
                    </td>
                  </tr>
                )}
              </React.Fragment>
            ))}
          </tbody>
        </table>
      </div>

      <div className="al-pagination">
        <span className="al-muted">{total} log entries</span>
        <div className="al-page-btns">
          <Btn size="sm" variant="secondary" disabled={page<=1}          onClick={() => setPage(p=>p-1)}>← Prev</Btn>
          <span>Page {page} / {totalPages||1}</span>
          <Btn size="sm" variant="secondary" disabled={page>=totalPages} onClick={() => setPage(p=>p+1)}>Next →</Btn>
        </div>
      </div>
    </div>
  );
}

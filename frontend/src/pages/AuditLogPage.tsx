import { useState } from 'react';
import { useAuditLogs } from '../hooks/useAudit';

export default function AuditLogPage() {
  const [page, setPage] = useState(1);
  const [search, setSearch] = useState('');
  const [module, setModule] = useState('');

  const { data, isLoading } = useAuditLogs({ page, search: search || undefined, module: module || undefined });

  return (
    <div>
      <div className="page-header">
        <div>
          <h1 className="page-title">Audit Logs</h1>
          <p className="page-subtitle">Immutable system-wide activity log — all user actions are recorded</p>
        </div>
      </div>

      <div className="search-bar">
        <input
          type="text"
          placeholder="Search by user, description, entity\u2026"
          value={search}
          onChange={(e) => { setSearch(e.target.value); setPage(1); }}
        />
        <select value={module} onChange={(e) => { setModule(e.target.value); setPage(1); }} style={{ width: 'auto' }}>
          <option value="">All Modules</option>
          <option value="EDMS">EDMS</option>
          <option value="WORKFLOW">Workflow</option>
          <option value="OCR">OCR</option>
          <option value="CORE">Core</option>
          <option value="AUTH">Auth</option>
        </select>
      </div>

      <div className="data-table-wrap">
        <table>
          <thead>
            <tr>
              <th>Timestamp</th>
              <th>User</th>
              <th>Module</th>
              <th>Action</th>
              <th>Entity</th>
              <th>Description</th>
              <th>IP</th>
              <th>Success</th>
            </tr>
          </thead>
          <tbody>
            {isLoading && <tr><td colSpan={8} style={{ textAlign: 'center', padding: '2rem' }}>Loading\u2026</td></tr>}
            {(data?.results ?? []).map((log) => (
              <tr key={log.id}>
                <td style={{ fontSize: 'var(--font-size-xs)', fontFamily: 'var(--font-family-mono)', whiteSpace: 'nowrap' }}>
                  {new Date(log.timestamp).toLocaleString('en-IN')}
                </td>
                <td style={{ fontSize: 'var(--font-size-xs)' }}>
                  <span style={{ fontWeight: 600 }}>{log.username}</span>
                  {log.user_full_name && <><br /><span style={{ color: 'var(--color-neutral-500)' }}>{log.user_full_name}</span></>}
                </td>
                <td><span style={{ fontSize: 'var(--font-size-xs)', fontWeight: 600, textTransform: 'uppercase', color: 'var(--color-iris-80)' }}>{log.module}</span></td>
                <td style={{ fontFamily: 'var(--font-family-mono)', fontSize: 'var(--font-size-xs)' }}>{log.action}</td>
                <td style={{ fontSize: 'var(--font-size-xs)' }}>
                  <span style={{ color: 'var(--color-neutral-500)' }}>{log.entity_type}</span>
                  <br />{log.entity_identifier}
                </td>
                <td style={{ fontSize: 'var(--font-size-xs)', maxWidth: 240, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{log.description}</td>
                <td style={{ fontSize: 'var(--font-size-xs)', fontFamily: 'var(--font-family-mono)' }}>{log.ip_address ?? '\u2014'}</td>
                <td>
                  <span style={{ fontSize: '1rem' }}>{log.success ? '\u2705' : '\u274C'}</span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div className="pagination">
        <span>Total: {data?.count ?? 0}</span>
        <button className="btn btn-secondary" onClick={() => setPage((p) => Math.max(1, p - 1))} disabled={!data?.previous}>\u2190 Prev</button>
        <span>Page {page}</span>
        <button className="btn btn-secondary" onClick={() => setPage((p) => p + 1)} disabled={!data?.next}>Next \u2192</button>
      </div>
    </div>
  );
}

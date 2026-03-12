import { useState } from 'react';
import { useWorkLedger } from '../hooks/useWorkLedger';
import type { WorkLedgerStatus } from '../api/types';

const statusBadge = (s: WorkLedgerStatus) => {
  const map: Record<WorkLedgerStatus, string> = {
    OPEN: 'open', IN_PROGRESS: 'processing', CLOSED: 'closed', ON_HOLD: 'draft'
  };
  return `badge badge-${map[s] ?? 'draft'}`;
};

export default function WorkLedgerPage() {
  const [page, setPage] = useState(1);
  const [status, setStatus] = useState('');
  const [search, setSearch] = useState('');

  const { data, isLoading } = useWorkLedger({ page, status: status || undefined, search: search || undefined });

  return (
    <div>
      <div className="page-header">
        <div>
          <h1 className="page-title">Work Ledger</h1>
          <p className="page-subtitle">Track incoming technical work — eOffice, tenders, drawing reviews</p>
        </div>
      </div>

      <div className="search-bar">
        <input
          type="text"
          placeholder="Search by subject, eOffice no., vendor\u2026"
          value={search}
          onChange={(e) => { setSearch(e.target.value); setPage(1); }}
        />
        <select value={status} onChange={(e) => { setStatus(e.target.value); setPage(1); }} style={{ width: 'auto' }}>
          <option value="">All Status</option>
          <option value="OPEN">Open</option>
          <option value="IN_PROGRESS">In Progress</option>
          <option value="ON_HOLD">On Hold</option>
          <option value="CLOSED">Closed</option>
        </select>
      </div>

      <div className="data-table-wrap">
        <table>
          <thead>
            <tr>
              <th>#</th>
              <th>Subject</th>
              <th>Work Type</th>
              <th>Section</th>
              <th>Assigned To</th>
              <th>eOffice No.</th>
              <th>Status</th>
              <th>Target Date</th>
            </tr>
          </thead>
          <tbody>
            {isLoading && <tr><td colSpan={8} style={{ textAlign: 'center', padding: '2rem' }}>Loading\u2026</td></tr>}
            {!isLoading && (data?.results ?? []).length === 0 && (
              <tr><td colSpan={8} style={{ textAlign: 'center', padding: '2rem', color: 'var(--color-neutral-500)' }}>No work entries found.</td></tr>
            )}
            {(data?.results ?? []).map((entry) => (
              <tr key={entry.id}>
                <td style={{ fontFamily: 'var(--font-family-mono)', fontSize: 'var(--font-size-xs)' }}>{entry.id}</td>
                <td style={{ maxWidth: 260, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{entry.subject || entry.eoffice_subject || '\u2014'}</td>
                <td>{entry.work_type_name ?? '\u2014'}</td>
                <td>{entry.section_name ?? '\u2014'}</td>
                <td>{entry.assigned_to_name ?? '\u2014'}</td>
                <td style={{ fontFamily: 'var(--font-family-mono)', fontSize: 'var(--font-size-xs)' }}>{entry.eoffice_file_number || '\u2014'}</td>
                <td><span className={statusBadge(entry.status)}>{entry.status.replace('_', ' ')}</span></td>
                <td style={{ fontSize: 'var(--font-size-xs)', color: entry.target_date && new Date(entry.target_date) < new Date() ? 'var(--color-error)' : 'var(--color-neutral-500)' }}>
                  {entry.target_date ? new Date(entry.target_date).toLocaleDateString('en-IN') : '\u2014'}
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

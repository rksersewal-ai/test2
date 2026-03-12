import { useState } from 'react';
import { Link } from 'react-router-dom';
import { useDocuments } from '../hooks/useDocuments';
import type { DocumentStatus } from '../api/types';

const statusBadge = (s: DocumentStatus) => {
  const map: Record<DocumentStatus, string> = {
    ACTIVE: 'active', DRAFT: 'draft', OBSOLETE: 'obsolete', SUPERSEDED: 'superseded'
  };
  return `badge badge-${map[s] ?? 'draft'}`;
};

export default function DocumentListPage() {
  const [page, setPage] = useState(1);
  const [search, setSearch] = useState('');
  const [status, setStatus] = useState('');

  const { data, isLoading } = useDocuments({ page, search: search || undefined, status: status || undefined });

  return (
    <div>
      <div className="page-header">
        <div>
          <h1 className="page-title">Documents</h1>
          <p className="page-subtitle">All controlled engineering documents in EDMS</p>
        </div>
      </div>

      <div className="search-bar">
        <input
          type="text"
          placeholder="Search by document number, title, keywords\u2026"
          value={search}
          onChange={(e) => { setSearch(e.target.value); setPage(1); }}
        />
        <select value={status} onChange={(e) => { setStatus(e.target.value); setPage(1); }} style={{ width: 'auto' }}>
          <option value="">All Status</option>
          <option value="ACTIVE">Active</option>
          <option value="DRAFT">Draft</option>
          <option value="SUPERSEDED">Superseded</option>
          <option value="OBSOLETE">Obsolete</option>
        </select>
      </div>

      <div className="data-table-wrap">
        <table>
          <thead>
            <tr>
              <th>Document No.</th>
              <th>Title</th>
              <th>Category</th>
              <th>Section</th>
              <th>Standard</th>
              <th>Rev.</th>
              <th>Status</th>
              <th>Updated</th>
            </tr>
          </thead>
          <tbody>
            {isLoading && (
              <tr><td colSpan={8} style={{ textAlign: 'center', padding: '2rem', color: 'var(--color-neutral-500)' }}>Loading\u2026</td></tr>
            )}
            {!isLoading && (data?.results ?? []).length === 0 && (
              <tr><td colSpan={8} style={{ textAlign: 'center', padding: '2rem', color: 'var(--color-neutral-500)' }}>No documents found.</td></tr>
            )}
            {(data?.results ?? []).map((doc) => (
              <tr key={doc.id}>
                <td><Link to={`/documents/${doc.id}`}>{doc.document_number}</Link></td>
                <td style={{ maxWidth: 260, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{doc.title}</td>
                <td>{doc.category_name ?? '\u2014'}</td>
                <td>{doc.section_name ?? '\u2014'}</td>
                <td>{doc.source_standard || '\u2014'}</td>
                <td>{doc.revision_count}</td>
                <td><span className={statusBadge(doc.status)}>{doc.status}</span></td>
                <td style={{ fontSize: 'var(--font-size-xs)', color: 'var(--color-neutral-500)' }}>
                  {new Date(doc.updated_at).toLocaleDateString('en-IN')}
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

import { useParams, Link } from 'react-router-dom';
import { useDocument } from '../hooks/useDocuments';
import type { Revision } from '../api/types';

function RevisionRow({ rev }: { rev: Revision }) {
  return (
    <tr>
      <td>{rev.revision_number}</td>
      <td>{rev.revision_date ?? '\u2014'}</td>
      <td><span className={`badge badge-${rev.status === 'CURRENT' ? 'active' : 'superseded'}`}>{rev.status}</span></td>
      <td>{rev.change_description || '\u2014'}</td>
      <td>{rev.eoffice_ref || '\u2014'}</td>
      <td>{rev.files.length} file(s)</td>
    </tr>
  );
}

export default function DocumentDetailPage() {
  const { id } = useParams<{ id: string }>();
  const { data: doc, isLoading, error } = useDocument(Number(id));

  if (isLoading) return <div className="empty-state"><h2>Loading\u2026</h2></div>;
  if (error || !doc) return <div className="empty-state"><h2>Document not found</h2><p><Link to="/documents">\u2190 Back</Link></p></div>;

  return (
    <div>
      <div className="page-header">
        <div>
          <p style={{ fontSize: 'var(--font-size-sm)', color: 'var(--color-neutral-500)', marginBottom: 'var(--space-1)' }}>
            <Link to="/documents">\u2190 Documents</Link>
          </p>
          <h1 className="page-title">{doc.document_number}</h1>
          <p className="page-subtitle">{doc.title}</p>
        </div>
        <span className={`badge badge-${doc.status.toLowerCase()}`}>{doc.status}</span>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 'var(--space-5)', marginBottom: 'var(--space-6)' }}>
        <div className="card">
          <h2 style={{ marginBottom: 'var(--space-4)' }}>Document Info</h2>
          <dl style={{ display: 'grid', gridTemplateColumns: 'max-content 1fr', gap: 'var(--space-2) var(--space-4)' }}>
            {[
              ['Category', doc.category_name],
              ['Section', doc.section_name],
              ['Standard', doc.source_standard],
              ['eOffice No.', doc.eoffice_file_number],
              ['eOffice Subject', doc.eoffice_subject],
              ['Keywords', doc.keywords],
              ['Created By', doc.created_by_name],
              ['Created At', new Date(doc.created_at).toLocaleString('en-IN')],
            ].map(([k, v]) => (
              <>
                <dt style={{ fontSize: 'var(--font-size-sm)', fontWeight: 600, color: 'var(--color-neutral-500)' }}>{k}</dt>
                <dd style={{ fontSize: 'var(--font-size-sm)', color: 'var(--color-neutral-900)' }}>{v || '\u2014'}</dd>
              </>
            ))}
          </dl>
        </div>
        <div className="card">
          <h2 style={{ marginBottom: 'var(--space-4)' }}>Description</h2>
          <p style={{ fontSize: 'var(--font-size-sm)', color: 'var(--color-neutral-700)', lineHeight: 1.6 }}>
            {doc.description || 'No description provided.'}
          </p>
        </div>
      </div>

      <div className="card">
        <h2 style={{ marginBottom: 'var(--space-4)' }}>Revision History ({doc.revisions.length})</h2>
        <div className="data-table-wrap">
          <table>
            <thead>
              <tr>
                <th>Rev. No.</th>
                <th>Date</th>
                <th>Status</th>
                <th>Change Description</th>
                <th>eOffice Ref</th>
                <th>Files</th>
              </tr>
            </thead>
            <tbody>
              {doc.revisions.length === 0 && (
                <tr><td colSpan={6} style={{ textAlign: 'center', color: 'var(--color-neutral-500)' }}>No revisions recorded.</td></tr>
              )}
              {doc.revisions.map((rev) => <RevisionRow key={rev.id} rev={rev} />)}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}

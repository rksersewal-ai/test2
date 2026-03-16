// =============================================================================
// FILE: frontend/src/pages/DocumentDetailPage.tsx
// BUG FIX 1: handleDownload used doc?.title as filename — no file extension.
//            Now appends the extension from doc.file_url or defaults to .pdf
// BUG FIX 2: 'Supersede' action in ConfirmDialog showed an info toast but
//            left the dialog open (confirm state not cleared). Fixed.
// BUG FIX 3: useEffect dependency was docId which is a derived value from
//            useParams. Should use id (string) to avoid stale closure.
// =============================================================================
import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { PageHeader, Btn, ConfirmDialog, Toast } from '../components/common';
import type { ToastMsg } from '../components/common';
import { documentService } from '../services/documentService';
import { usePreviewTabs } from '../context/PreviewTabsContext';
import './DocumentDetailPage.css';

export default function DocumentDetailPage() {
  const { id }   = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { openTab } = usePreviewTabs();
  const docId    = Number(id);

  const [doc,          setDoc]          = useState<any>(null);
  const [versions,     setVersions]     = useState<any[]>([]);
  const [loading,      setLoading]      = useState(true);
  const [toast,        setToast]        = useState<ToastMsg | null>(null);
  const [confirm,      setConfirm]      = useState<{ action: 'delete' | 'approve' | 'reject' | 'supersede'; label: string } | null>(null);
  const [rejectReason, setRejectReason] = useState('');
  const [showReject,   setShowReject]   = useState(false);
  const [downloading,  setDownloading]  = useState(false);

  const load = async () => {
    setLoading(true);
    try {
      const [d, v] = await Promise.all([
        documentService.get(docId),
        documentService.listVersions(docId).catch(() => []),
      ]);
      setDoc(d);
      setVersions(Array.isArray(v) ? v : (v as any).results ?? []);
    } catch {
      setToast({ type: 'error', text: 'Document not found.' });
    } finally {
      setLoading(false);
    }
  };

  // BUG FIX 3: id (string from useParams) as dep, not the derived docId
  useEffect(() => { load(); }, [id]);

  const handleDownload = async () => {
    setDownloading(true);
    try {
      const blob = await documentService.downloadFile(docId);
      const url  = URL.createObjectURL(blob);
      const a    = document.createElement('a');
      a.href     = url;
      // BUG FIX 1: include file extension in download filename
      const ext  = doc?.file_url?.split('.').pop()?.toLowerCase() ?? 'pdf';
      const safe = (doc?.title ?? `document_${docId}`).replace(/[<>:"/\\|?*]/g, '_');
      a.download = `${safe}.${ext}`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    } catch {
      setToast({ type: 'error', text: 'Download failed.' });
    } finally {
      setDownloading(false);
    }
  };

  const handleConfirm = async () => {
    if (!confirm) return;
    try {
      if (confirm.action === 'delete')    { await documentService.delete(docId);  navigate('/documents'); }
      if (confirm.action === 'approve')   { await documentService.approve(docId); load(); setToast({ type: 'success', text: 'Document approved.' }); }
      if (confirm.action === 'supersede') { setToast({ type: 'info', text: 'Supersede: open the new document and link from there.' }); }
    } catch {
      setToast({ type: 'error', text: `${confirm.action} failed.` });
    } finally {
      setConfirm(null); // BUG FIX 2: always clear confirm (was missing for supersede)
    }
  };

  const handleReject = async () => {
    try {
      await documentService.reject(docId, rejectReason);
      setToast({ type: 'success', text: 'Document rejected.' });
      setShowReject(false);
      setRejectReason('');
      load();
    } catch {
      setToast({ type: 'error', text: 'Reject failed.' });
    }
  };

  if (loading) return <div className="ddetail-loading">⏳ Loading…</div>;
  if (!doc)    return (
    <div className="ddetail-loading">
      ⚠️ Document not found.
      <Btn variant="ghost" onClick={() => navigate('/documents')}>← Back</Btn>
    </div>
  );

  const canApprove = doc.status === 'PENDING_REVIEW' || doc.status === 'DRAFT';
  const canReject  = doc.status === 'PENDING_REVIEW';

  return (
    <div className="ddetail-page">
      <PageHeader
        title={doc.document_number ?? doc.title}
        subtitle={doc.title}
        back={() => navigate('/documents')}
      >
        <Btn size="sm" variant="secondary" onClick={() => {
          openTab({
            id: `doc-${docId}`,
            docNumber: doc?.document_number ?? doc?.drawing_number ?? `DOC-${docId}`,
            title: doc?.title ?? `Document ${docId}`,
            fileUrl: doc?.file_url ?? `/api/v1/edms/documents/${docId}/file/`,
            fileId: docId,
            documentId: docId,
            pageCount: 1,
            mimeType: 'application/pdf',
          });
          navigate('/preview');
        }}>
          📄 Preview
        </Btn>
        <Btn size="sm" variant="secondary" loading={downloading} onClick={handleDownload}>
          ⬇ Download
        </Btn>
        {canApprove && (
          <Btn size="sm" variant="primary" onClick={() => setConfirm({ action: 'approve', label: 'Approve this document?' })}>
            ✅ Approve
          </Btn>
        )}
        {canReject && (
          <Btn size="sm" variant="danger" onClick={() => setShowReject(true)}>
            ❌ Reject
          </Btn>
        )}
        <Btn size="sm" variant="danger" onClick={() => setConfirm({ action: 'delete', label: 'Permanently delete this document?' })}>
          🗑 Delete
        </Btn>
      </PageHeader>

      <Toast msg={toast} onClose={() => setToast(null)} />

      <ConfirmDialog
        open={!!confirm}
        title={confirm?.action === 'delete' ? 'Delete Document' : 'Confirm Action'}
        message={confirm?.label ?? ''}
        confirmLabel={confirm?.action === 'delete' ? 'Delete' : 'Confirm'}
        onConfirm={handleConfirm}
        onCancel={() => setConfirm(null)}
      />

      {showReject && (
        <div className="ddetail-overlay" onClick={() => setShowReject(false)}>
          <div className="ddetail-modal" onClick={e => e.stopPropagation()}>
            <div className="ddetail-modal-title">❌ Reject Document</div>
            <p style={{ fontSize: 13, color: '#555', marginBottom: 10 }}>Provide a reason for rejection:</p>
            <textarea
              className="ddetail-textarea" rows={4}
              value={rejectReason}
              onChange={e => setRejectReason(e.target.value)}
              placeholder="Reason for rejection…"
            />
            <div className="ddetail-modal-btns">
              <Btn variant="secondary" size="sm" onClick={() => setShowReject(false)}>Cancel</Btn>
              <Btn variant="danger"    size="sm" onClick={handleReject} disabled={!rejectReason.trim()}>❌ Reject</Btn>
            </div>
          </div>
        </div>
      )}

      <div className="ddetail-grid">
        <div className="ddetail-card">
          <div className="ddetail-card-title">📋 Document Info</div>
          <div className="ddetail-card-body">
            <table className="ddetail-meta-table">
              <tbody>
                {([
                  ['Status',        <span className={`ddetail-badge ddetail-badge-${doc.status?.toLowerCase()}`}>{doc.status?.replace('_', ' ')}</span>],
                  ['Document No.',  <span className="ddetail-mono">{doc.document_number ?? '\u2014'}</span>],
                  ['Document Type', doc.document_type ?? doc.doc_type ?? '\u2014'],
                  ['Version',       doc.version ?? doc.revision ?? '\u2014'],
                  ['Category',      doc.category_name ?? '\u2014'],
                  ['Section',       doc.section_name ?? '\u2014'],
                  ['eOffice No.',   doc.eoffice_file_number ?? '\u2014'],
                  ['eOffice Sub.',  doc.eoffice_subject ?? '\u2014'],
                  ['Keywords',      doc.keywords ?? '\u2014'],
                  ['Created By',    doc.created_by_name ?? '\u2014'],
                  ['Created At',    doc.created_at ? new Date(doc.created_at).toLocaleString('en-IN') : '\u2014'],
                  ['Updated At',    doc.updated_at ? new Date(doc.updated_at).toLocaleString('en-IN') : '\u2014'],
                ] as [string, React.ReactNode][]).map(([k, v], i) => (
                  <tr key={i}>
                    <td className="ddetail-meta-key">{k}</td>
                    <td className="ddetail-meta-val">{v}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        <div className="ddetail-card">
          <div className="ddetail-card-title">📝 Description</div>
          <div className="ddetail-card-body">
            <p className="ddetail-desc-text">{doc.description || 'No description provided.'}</p>
            {doc.tags?.length > 0 && (
              <div className="ddetail-tags">
                {doc.tags.map((t: any, i: number) => (
                  <span key={i} className="ddetail-tag">{typeof t === 'string' ? t : t.name}</span>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>

      <div className="ddetail-card ddetail-versions">
        <div className="ddetail-card-title">🔄 Version / Revision History ({versions.length})</div>
        <div className="ddetail-card-body">
          {versions.length === 0
            ? <div className="ddetail-no-versions">No version history recorded.</div>
            : (
              <table className="ddetail-ver-table">
                <thead><tr>
                  <th>Rev. / Version</th><th>Date</th><th>Status</th>
                  <th>Change Description</th><th>eOffice Ref</th><th>Files</th>
                </tr></thead>
                <tbody>
                  {versions.map((v: any, i: number) => (
                    <tr key={i}>
                      <td className="ddetail-mono">{v.revision_number ?? v.version ?? '\u2014'}</td>
                      <td className="ddetail-muted">{v.revision_date ?? v.date ?? '\u2014'}</td>
                      <td><span className={`ddetail-badge ddetail-badge-${(v.status ?? '').toLowerCase()}`}>{v.status}</span></td>
                      <td className="ddetail-desc">{v.change_description ?? '\u2014'}</td>
                      <td className="ddetail-mono ddetail-muted">{v.eoffice_ref ?? '\u2014'}</td>
                      <td className="ddetail-muted">{v.files?.length ?? 0} file(s)</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )
          }
        </div>
      </div>
    </div>
  );
}

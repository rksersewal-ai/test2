// =============================================================================
// FILE: frontend/src/pages/DocumentDetailPage.tsx  (Phase 3 — full detail +
// approve / reject / supersede / download / version history)
// =============================================================================
import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { PageHeader, Btn, ConfirmDialog, Toast } from '../components/common';
import type { ToastMsg } from '../components/common';
import { documentService } from '../services/documentService';
import './DocumentDetailPage.css';

export default function DocumentDetailPage() {
  const { id }    = useParams<{ id: string }>();
  const navigate  = useNavigate();
  const docId     = Number(id);

  const [doc,      setDoc]      = useState<any>(null);
  const [versions, setVersions] = useState<any[]>([]);
  const [loading,  setLoading]  = useState(true);
  const [toast,    setToast]    = useState<ToastMsg|null>(null);
  const [confirm,  setConfirm]  = useState<{ action:'delete'|'approve'|'reject'|'supersede'; label:string }|null>(null);
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
      setVersions(Array.isArray(v) ? v : v.results ?? []);
    } catch { setToast({ type:'error', text:'Document not found.' }); }
    finally { setLoading(false); }
  };

  useEffect(() => { load(); }, [docId]);

  const handleDownload = async () => {
    setDownloading(true);
    try {
      const blob = await documentService.downloadFile(docId);
      const url  = URL.createObjectURL(blob);
      const a    = document.createElement('a');
      a.href     = url;
      a.download = doc?.title ?? `document_${docId}`;
      a.click();
      URL.revokeObjectURL(url);
    } catch { setToast({ type:'error', text:'Download failed.' }); }
    finally { setDownloading(false); }
  };

  const handleConfirm = async () => {
    if (!confirm) return;
    try {
      if (confirm.action === 'delete')   { await documentService.delete(docId);   navigate('/documents'); }
      if (confirm.action === 'approve')  { await documentService.approve(docId);  load(); setToast({ type:'success', text:'Document approved.' }); }
      if (confirm.action === 'supersede'){ setToast({ type:'info', text:'Supersede: open the new document and link from there.' }); }
    } catch { setToast({ type:'error', text:`${confirm.action} failed.` }); }
    finally { setConfirm(null); }
  };

  const handleReject = async () => {
    try {
      await documentService.reject(docId, rejectReason);
      setToast({ type:'success', text:'Document rejected.' });
      setShowReject(false); setRejectReason(''); load();
    } catch { setToast({ type:'error', text:'Reject failed.' }); }
  };

  if (loading) return <div className="ddetail-loading">⏳ Loading…</div>;
  if (!doc)    return (
    <div className="ddetail-loading">
      ⚠️ Document not found. <Btn variant="ghost" onClick={() => navigate('/documents')}>← Back</Btn>
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
        {/* Action buttons */}
        <Btn size="sm" variant="secondary" onClick={() => navigate(`/documents/${docId}/preview`)}>
          📄 Preview
        </Btn>
        <Btn size="sm" variant="secondary" loading={downloading} onClick={handleDownload}>
          ⬇ Download
        </Btn>
        {canApprove && (
          <Btn size="sm" variant="primary"
            onClick={() => setConfirm({ action:'approve', label:'Approve this document?' })}>
            ✅ Approve
          </Btn>
        )}
        {canReject && (
          <Btn size="sm" variant="danger" onClick={() => setShowReject(true)}>
            ❌ Reject
          </Btn>
        )}
        <Btn size="sm" variant="danger"
          onClick={() => setConfirm({ action:'delete', label:'Permanently delete this document?' })}>
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

      {/* Reject modal */}
      {showReject && (
        <div className="ddetail-overlay" onClick={() => setShowReject(false)}>
          <div className="ddetail-modal" onClick={e => e.stopPropagation()}>
            <div className="ddetail-modal-title">❌ Reject Document</div>
            <p style={{fontSize:13, color:'#555', marginBottom:10}}>Provide a reason for rejection:</p>
            <textarea className="ddetail-textarea" rows={4}
              value={rejectReason} onChange={e => setRejectReason(e.target.value)}
              placeholder="Reason for rejection…" />
            <div className="ddetail-modal-btns">
              <Btn variant="secondary" size="sm" onClick={() => setShowReject(false)}>Cancel</Btn>
              <Btn variant="danger"    size="sm" onClick={handleReject} disabled={!rejectReason.trim()}>❌ Reject</Btn>
            </div>
          </div>
        </div>
      )}

      {/* Two-column info */}
      <div className="ddetail-grid">
        {/* Left: metadata */}
        <div className="ddetail-card">
          <div className="ddetail-card-title">📋 Document Info</div>
          <div className="ddetail-card-body">
            <table className="ddetail-meta-table">
              <tbody>
                {[
                  ['Status',        <span className={`ddetail-badge ddetail-badge-${doc.status?.toLowerCase()}`}>{doc.status?.replace('_',' ')}</span>],
                  ['Document No.',  <span className="ddetail-mono">{doc.document_number ?? '—'}</span>],
                  ['Document Type', doc.document_type ?? doc.doc_type ?? '—'],
                  ['Version',       doc.version ?? doc.revision ?? '—'],
                  ['Category',      doc.category_name ?? '—'],
                  ['Section',       doc.section_name ?? '—'],
                  ['eOffice No.',   doc.eoffice_file_number ?? '—'],
                  ['eOffice Sub.',  doc.eoffice_subject ?? '—'],
                  ['Keywords',      doc.keywords ?? '—'],
                  ['Created By',    doc.created_by_name ?? '—'],
                  ['Created At',    doc.created_at ? new Date(doc.created_at).toLocaleString('en-IN') : '—'],
                  ['Updated At',    doc.updated_at ? new Date(doc.updated_at).toLocaleString('en-IN') : '—'],
                ].map(([k, v], i) => (
                  <tr key={i}>
                    <td className="ddetail-meta-key">{k}</td>
                    <td className="ddetail-meta-val">{v}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* Right: description */}
        <div className="ddetail-card">
          <div className="ddetail-card-title">📝 Description</div>
          <div className="ddetail-card-body">
            <p className="ddetail-desc-text">{doc.description || 'No description provided.'}</p>
            {doc.tags?.length > 0 && (
              <div className="ddetail-tags">
                {doc.tags.map((t: any, i: number) => (
                  <span key={i} className="ddetail-tag">{t.name ?? t}</span>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Version history */}
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
                      <td className="ddetail-mono">{v.revision_number ?? v.version ?? '—'}</td>
                      <td className="ddetail-muted">{v.revision_date ?? v.date ?? '—'}</td>
                      <td><span className={`ddetail-badge ddetail-badge-${(v.status??'').toLowerCase()}`}>{v.status}</span></td>
                      <td className="ddetail-desc">{v.change_description ?? '—'}</td>
                      <td className="ddetail-mono ddetail-muted">{v.eoffice_ref ?? '—'}</td>
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

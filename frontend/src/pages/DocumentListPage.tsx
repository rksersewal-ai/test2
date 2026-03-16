// =============================================================================
// FILE: frontend/src/pages/DocumentListPage.tsx  (Phase 2 — full list + upload)
// =============================================================================
import React, { useState, useEffect, useCallback, useRef } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { PageHeader, Btn, SearchBar, ConfirmDialog, Toast } from '../components/common';
import type { ToastMsg } from '../components/common';
import { documentService } from '../services/documentService';
import { usePreviewTabs } from '../context/PreviewTabsContext';
import './DocumentListPage.css';

const STATUS_CLASS: Record<string,string> = {
  DRAFT:'doc-badge-draft', PENDING_REVIEW:'doc-badge-review',
  APPROVED:'doc-badge-approved', OBSOLETE:'doc-badge-obsolete',
  REJECTED:'doc-badge-rejected',
};

export default function DocumentListPage() {
  const [docs,       setDocs]       = useState<any[]>([]);
  const [total,      setTotal]      = useState(0);
  const [page,       setPage]       = useState(1);
  const [loading,    setLoading]    = useState(false);
  const [toast,      setToast]      = useState<ToastMsg|null>(null);
  const [confirm,    setConfirm]    = useState<number|null>(null);
  const [showUpload, setShowUpload] = useState(false);
  const [search,     setSearch]     = useState('');
  const [searchParams] = useSearchParams();
  const [status,     setStatus]     = useState(searchParams.get('status') ?? '');
  const navigate = useNavigate();
  const { openTab } = usePreviewTabs();
  const PAGE_SIZE = 20;

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const p: Record<string,string> = { page: String(page), page_size: String(PAGE_SIZE) };
      if (search) p.q = search;
      if (status) p.status = status;
      const data = await documentService.list(p);
      setDocs(data.results ?? data);
      setTotal(data.count ?? data.total_count ?? 0);
    } catch { setToast({ type:'error', text:'Failed to load documents.' }); }
    finally { setLoading(false); }
  }, [page, search, status]);

  useEffect(() => { load(); }, [load]);

  const handleDelete = async () => {
    if (!confirm) return;
    try { await documentService.delete(confirm); setToast({ type:'success', text:'Document deleted.' }); load(); }
    catch { setToast({ type:'error', text:'Delete failed.' }); }
    finally { setConfirm(null); }
  };

  const totalPages = Math.ceil(total / PAGE_SIZE);

  return (
    <div className="doc-list-page">
      <PageHeader title="Documents" subtitle="Controlled engineering documents — drawings, specs, manuals">
        <Btn size="sm" onClick={() => setShowUpload(true)}>⬆ Upload Document</Btn>
      </PageHeader>

      <Toast msg={toast} onClose={() => setToast(null)} />
      <ConfirmDialog
        open={!!confirm}
        title="Delete Document" message="Permanently delete this document? This cannot be undone."
        confirmLabel="Delete"
        onConfirm={handleDelete} onCancel={() => setConfirm(null)}
      />

      {showUpload && (
        <UploadModal
          onClose={() => setShowUpload(false)}
          onSuccess={() => { setShowUpload(false); load(); setToast({ type:'success', text:'Document uploaded successfully.' }); }}
        />
      )}

      {/* Filters */}
      <div className="doc-toolbar">
        <SearchBar value={search} onChange={v => { setSearch(v); setPage(1); }} placeholder="Search title, drawing no, PL number…" width={320} />
        <select value={status} onChange={e => { setStatus(e.target.value); setPage(1); }}>
          <option value="">All Status</option>
          <option value="DRAFT">Draft</option>
          <option value="PENDING_REVIEW">Pending Review</option>
          <option value="APPROVED">Approved</option>
          <option value="OBSOLETE">Obsolete</option>
          <option value="REJECTED">Rejected</option>
        </select>
        <Btn size="sm" variant="ghost" onClick={load}>↺ Refresh</Btn>
      </div>

      {/* Table */}
      <div className="doc-table-wrap">
        <table className="doc-table">
          <thead><tr>
            <th>Title</th><th>Doc No.</th><th>Type</th>
            <th>Status</th><th>Version</th><th>Modified</th><th>Actions</th>
          </tr></thead>
          <tbody>
            {loading && <tr><td colSpan={7} className="doc-center doc-muted">Loading…</td></tr>}
            {!loading && docs.length===0 && <tr><td colSpan={7} className="doc-center doc-muted">No documents found.</td></tr>}
            {docs.map(d => (
              <tr key={d.id}>
                <td className="doc-title" title={d.title}>{d.title}</td>
                <td className="doc-mono">{d.document_number ?? d.drawing_number ?? '—'}</td>
                <td className="doc-muted">{d.document_type ?? d.doc_type ?? '—'}</td>
                <td><span className={`doc-badge ${STATUS_CLASS[d.status] ?? ''}`}>{d.status?.replace('_',' ')}</span></td>
                <td className="doc-center doc-muted">{d.version ?? d.revision ?? '—'}</td>
                <td className="doc-muted" style={{fontSize:11}}>{d.updated_at ? new Date(d.updated_at).toLocaleDateString('en-IN') : '—'}</td>
                <td className="doc-actions">
                  <Btn size="sm" variant="ghost"    onClick={() => navigate(`/documents/${d.id}`)}>👁 View</Btn>
                  <Btn size="sm" variant="secondary" onClick={() => {
                      openTab({
                        id: `doc-${d.id}`,
                        docNumber: d.document_number ?? d.drawing_number ?? `DOC-${d.id}`,
                        title: d.title,
                        fileUrl: d.file_url ?? `/api/v1/edms/documents/${d.id}/file/`,
                        fileId: d.id,
                        documentId: d.id,
                        pageCount: 1,
                        mimeType: 'application/pdf',
                      });
                      navigate('/preview');
                  }}>📄 Preview</Btn>
                  <Btn size="sm" variant="danger"    onClick={() => setConfirm(d.id)}>🗑</Btn>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div className="doc-pagination">
        <span className="doc-muted">{total} documents</span>
        <div className="doc-page-btns">
          <Btn size="sm" variant="secondary" disabled={page<=1} onClick={() => setPage(p=>p-1)}>← Prev</Btn>
          <span>Page {page} / {totalPages||1}</span>
          <Btn size="sm" variant="secondary" disabled={page>=totalPages} onClick={() => setPage(p=>p+1)}>Next →</Btn>
        </div>
      </div>
    </div>
  );
}

// ─── Upload Modal ─────────────────────────────────────────────────────────────
function UploadModal({ onClose, onSuccess }: { onClose:()=>void; onSuccess:()=>void }) {
  const [form, setForm] = useState({
    title:'', document_number:'', document_type:'DRAWING',
    version:'A', description:'',
  });
  const [file,    setFile]    = useState<File|null>(null);
  const [saving,  setSaving]  = useState(false);
  const [errors,  setErrors]  = useState<Record<string,string>>({});
  const fileRef = useRef<HTMLInputElement>(null);

  const DOC_TYPES = ['DRAWING','SPECIFICATION','MANUAL','REPORT','CORRESPONDENCE','STANDARD','OTHER'];

  const validate = () => {
    const e: Record<string,string> = {};
    if (!form.title) e.title = 'Required';
    if (!file)       e.file  = 'Please select a file (PDF, DWG, DXF…)';
    setErrors(e);
    return Object.keys(e).length === 0;
  };

  const handleSave = async () => {
    if (!validate() || !file) return;
    setSaving(true);
    try {
      const fd = new FormData();
      Object.entries(form).forEach(([k,v]) => fd.append(k, v));
      fd.append('file', file);
      await documentService.create(fd);
      onSuccess();
    } catch (err: any) {
      setErrors({ _global: JSON.stringify(err?.response?.data ?? 'Upload failed.') });
    } finally { setSaving(false); }
  };

  const sf = (field: string, val: string) => { setForm(f => ({...f,[field]:val})); setErrors(e => ({...e,[field]:''})); };

  return (
    <div className="doc-modal-overlay" onClick={onClose}>
      <div className="doc-modal" onClick={e => e.stopPropagation()}>
        <div className="doc-modal-header">
          <span>⬆ Upload Document</span>
          <button className="doc-modal-close" onClick={onClose}>✕</button>
        </div>
        <div className="doc-modal-body">
          {errors._global && <div className="doc-alert-error">{errors._global}</div>}

          <div className="doc-form-grid">
            <div className="doc-field doc-full">
              <label>Title <span className="doc-req">*</span></label>
              <input type="text" value={form.title} onChange={e => sf('title', e.target.value)} placeholder="Document title…" />
              {errors.title && <span className="doc-err">{errors.title}</span>}
            </div>
            <div className="doc-field">
              <label>Document Number</label>
              <input type="text" value={form.document_number} onChange={e => sf('document_number', e.target.value)} placeholder="e.g. CLW/WAG9/TM/001" />
            </div>
            <div className="doc-field">
              <label>Document Type</label>
              <select value={form.document_type} onChange={e => sf('document_type', e.target.value)}>
                {DOC_TYPES.map(t => <option key={t} value={t}>{t}</option>)}
              </select>
            </div>
            <div className="doc-field">
              <label>Version / Revision</label>
              <input type="text" value={form.version} onChange={e => sf('version', e.target.value)} placeholder="A, 1.0, R2…" />
            </div>
            <div className="doc-field doc-full">
              <label>Description</label>
              <textarea rows={2} value={form.description} onChange={e => sf('description', e.target.value)} />
            </div>
            <div className="doc-field doc-full">
              <label>File <span className="doc-req">*</span></label>
              <div
                className={`doc-dropzone${file?' doc-dropzone--filled':''}`}
                onClick={() => fileRef.current?.click()}
                onDragOver={e => e.preventDefault()}
                onDrop={e => { e.preventDefault(); const f=e.dataTransfer.files[0]; if(f) setFile(f); }}
              >
                {file ? `📎 ${file.name} (${(file.size/1024).toFixed(1)} KB)` : '📂 Click or drag & drop PDF / DWG / DXF…'}
              </div>
              <input ref={fileRef} type="file" style={{display:'none'}}
                accept=".pdf,.dwg,.dxf,.xlsx,.docx,.png,.jpg"
                onChange={e => { const f=e.target.files?.[0]; if(f) setFile(f); }} />
              {errors.file && <span className="doc-err">{errors.file}</span>}
            </div>
          </div>
        </div>
        <div className="doc-modal-footer">
          <Btn variant="secondary" onClick={onClose} disabled={saving}>Cancel</Btn>
          <Btn variant="primary"   onClick={handleSave} loading={saving}>⬆ Upload</Btn>
        </div>
      </div>
    </div>
  );
}

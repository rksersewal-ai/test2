// =============================================================================
// FILE: frontend/src/pages/OCRQueuePage.tsx  (Phase 4 — real API)
// OCR queue management: view pending/failed jobs, retry, view extracted text
// =============================================================================
import React, { useState, useEffect, useCallback } from 'react';
import { PageHeader, Btn, SearchBar, Toast } from '../components/common';
import type { ToastMsg } from '../components/common';
import api from '../api/axios';
import './OCRQueuePage.css';

const BASE = '/ocr';

const ocrService = {
  list:    (params?: Record<string,string>) => api.get(`${BASE}/queue/`, { params }).then(r => r.data),
  retry:   (id: number) => api.post(`${BASE}/queue/${id}/retry/`).then(r => r.data),
  getText: (id: number) => api.get(`${BASE}/queue/${id}/text/`).then(r => r.data),
  dismiss: (id: number) => api.delete(`${BASE}/queue/${id}/`).then(r => r.data),
};

const STATUS_CLS: Record<string,string> = {
  PENDING:'ocr-badge-pending', PROCESSING:'ocr-badge-proc',
  COMPLETED:'ocr-badge-done',  FAILED:'ocr-badge-fail',
};

export default function OCRQueuePage() {
  const [items,       setItems]       = useState<any[]>([]);
  const [total,       setTotal]       = useState(0);
  const [page,        setPage]        = useState(1);
  const [search,      setSearch]      = useState('');
  const [status,      setStatus]      = useState('');
  const [loading,     setLoading]     = useState(false);
  const [toast,       setToast]       = useState<ToastMsg|null>(null);
  const [textModal,   setTextModal]   = useState<{id:number; text:string}|null>(null);
  const [loadingText, setLoadingText] = useState(false);
  const PAGE_SIZE = 25;

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const p: Record<string,string> = { page: String(page), page_size: String(PAGE_SIZE) };
      if (search) p.search = search;
      if (status) p.status = status;
      const data = await ocrService.list(p);
      setItems(data.results ?? data ?? []);
      setTotal(data.count ?? data.total_count ?? 0);
    } catch { setToast({ type:'error', text:'Failed to load OCR queue.' }); }
    finally  { setLoading(false); }
  }, [page, search, status]);

  useEffect(() => { load(); }, [load]);

  // Auto-refresh every 15s when there are PENDING/PROCESSING items
  useEffect(() => {
    const hasPending = items.some(i => i.status === 'PENDING' || i.status === 'PROCESSING');
    if (!hasPending) return;
    const t = setInterval(load, 15000);
    return () => clearInterval(t);
  }, [items, load]);

  const handleRetry = async (id: number) => {
    try   { await ocrService.retry(id); setToast({ type:'success', text:'Job re-queued.' }); load(); }
    catch { setToast({ type:'error', text:'Retry failed.' }); }
  };

  const handleDismiss = async (id: number) => {
    try   { await ocrService.dismiss(id); setToast({ type:'success', text:'Job dismissed.' }); load(); }
    catch { setToast({ type:'error', text:'Dismiss failed.' }); }
  };

  const handleViewText = async (id: number) => {
    setLoadingText(true);
    try {
      const data = await ocrService.getText(id);
      setTextModal({ id, text: data.text ?? data.extracted_text ?? '(No text extracted)' });
    } catch { setToast({ type:'error', text:'Could not load extracted text.' }); }
    finally  { setLoadingText(false); }
  };

  const totalPages = Math.ceil(total / PAGE_SIZE);

  return (
    <div className="ocr-page">
      <PageHeader title="OCR Queue" subtitle="Document text extraction jobs — status and retry management" />
      <Toast msg={toast} onClose={() => setToast(null)} />

      {/* Extracted text modal */}
      {textModal && (
        <div className="ocr-modal-overlay" onClick={() => setTextModal(null)}>
          <div className="ocr-modal" onClick={e => e.stopPropagation()}>
            <div className="ocr-modal-header">
              <span>📝 Extracted Text — Job #{textModal.id}</span>
              <button className="ocr-modal-close" onClick={() => setTextModal(null)}>✕</button>
            </div>
            <pre className="ocr-modal-text">{textModal.text}</pre>
          </div>
        </div>
      )}

      {/* Toolbar */}
      <div className="ocr-toolbar">
        <SearchBar value={search} onChange={v => { setSearch(v); setPage(1); }} placeholder="Search document title…" width={280} />
        <select className="ocr-select" value={status} onChange={e => { setStatus(e.target.value); setPage(1); }}>
          <option value="">All Status</option>
          <option value="PENDING">Pending</option>
          <option value="PROCESSING">Processing</option>
          <option value="COMPLETED">Completed</option>
          <option value="FAILED">Failed</option>
        </select>
        <Btn size="sm" variant="ghost" onClick={load}>↺ Refresh</Btn>
      </div>

      {/* Table */}
      <div className="ocr-table-wrap">
        <table className="ocr-table">
          <thead><tr>
            <th>#</th><th>Document</th><th>File</th><th>Engine</th>
            <th>Status</th><th>Queued At</th><th>Pages</th><th>Actions</th>
          </tr></thead>
          <tbody>
            {loading && <tr><td colSpan={8} className="ocr-center ocr-muted">Loading…</td></tr>}
            {!loading && items.length===0 && <tr><td colSpan={8} className="ocr-center ocr-muted">No jobs found.</td></tr>}
            {items.map(job => (
              <tr key={job.id}>
                <td className="ocr-mono ocr-muted">{job.id}</td>
                <td className="ocr-title" title={job.document_title}>{job.document_title ?? '—'}</td>
                <td className="ocr-mono ocr-muted" style={{fontSize:11}}>{job.file_name ?? '—'}</td>
                <td className="ocr-muted">{job.engine ?? 'Tesseract'}</td>
                <td>
                  <span className={`ocr-badge ${STATUS_CLS[job.status] ?? ''}`}>
                    {job.status === 'PROCESSING' ? '⚙️ ' : ''}{job.status}
                  </span>
                  {job.status === 'FAILED' && job.error_message && (
                    <div className="ocr-error-msg" title={job.error_message}>
                      {job.error_message.slice(0, 60)}{job.error_message.length > 60 ? '…' : ''}
                    </div>
                  )}
                </td>
                <td className="ocr-muted" style={{fontSize:11}}>
                  {job.created_at ? new Date(job.created_at).toLocaleString('en-IN') : '—'}
                </td>
                <td className="ocr-center ocr-muted">{job.page_count ?? '—'}</td>
                <td className="ocr-actions">
                  {job.status === 'COMPLETED' && (
                    <Btn size="sm" variant="ghost" loading={loadingText}
                      onClick={() => handleViewText(job.id)}>📝 Text</Btn>
                  )}
                  {job.status === 'FAILED' && (
                    <Btn size="sm" variant="primary" onClick={() => handleRetry(job.id)}>↺ Retry</Btn>
                  )}
                  {(job.status === 'FAILED' || job.status === 'COMPLETED') && (
                    <Btn size="sm" variant="danger" onClick={() => handleDismiss(job.id)}>🗑</Btn>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div className="ocr-pagination">
        <span className="ocr-muted">{total} jobs total</span>
        <div className="ocr-page-btns">
          <Btn size="sm" variant="secondary" disabled={page<=1}          onClick={() => setPage(p=>p-1)}>← Prev</Btn>
          <span>Page {page} / {totalPages||1}</span>
          <Btn size="sm" variant="secondary" disabled={page>=totalPages} onClick={() => setPage(p=>p+1)}>Next →</Btn>
        </div>
      </div>
    </div>
  );
}

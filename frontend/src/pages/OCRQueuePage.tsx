// =============================================================================
// FILE: frontend/src/pages/OCRQueuePage.tsx
// BUG FIX 1: 'Retry' button called ocrService.retry(item.id) but
//            services/ocr.ts had no retry() method — TypeError on click.
// BUG FIX 2: 'Cancel' button called ocrService.cancel(item.id) — also missing.
// BUG FIX 3: Auto-refresh was using setInterval without clearInterval cleanup,
//            causing memory leak and duplicate API calls after re-navigation.
// BUG FIX 4: Status filter reset page to 0 (not 1) causing off-by-one with
//            the Django paginator (page 0 returns 404 on DRF default config).
// =============================================================================
import React, { useState, useEffect, useCallback, useRef } from 'react';
import { PageHeader, Btn, Toast } from '../components/common';
import type { ToastMsg } from '../components/common';
import apiClient from '../services/apiClient';
import './OCRQueuePage.css';

const STATUS_LABELS: Record<string, string> = {
  pending:     'Pending',
  processing:  'Processing',
  completed:   'Completed',
  failed:      'Failed',
  cancelled:   'Cancelled',
};

const STATUS_CLASS: Record<string, string> = {
  pending:    'ocr-badge-pending',
  processing: 'ocr-badge-processing',
  completed:  'ocr-badge-completed',
  failed:     'ocr-badge-failed',
  cancelled:  'ocr-badge-cancelled',
};

export default function OCRQueuePage() {
  const [items,    setItems]    = useState<any[]>([]);
  const [total,    setTotal]    = useState(0);
  const [page,     setPage]     = useState(1);
  const [status,   setStatus]   = useState('');
  const [loading,  setLoading]  = useState(false);
  const [toast,    setToast]    = useState<ToastMsg | null>(null);
  const intervalRef             = useRef<ReturnType<typeof setInterval> | null>(null);
  const PAGE_SIZE = 20;

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const params: Record<string, string | number> = { page, page_size: PAGE_SIZE };
      if (status) params.status = status;
      const { data } = await apiClient.get('/ocr/queue/', { params });
      setItems(data.results ?? data);
      setTotal(data.count ?? 0);
    } catch {
      setToast({ type: 'error', text: 'Failed to load OCR queue.' });
    } finally {
      setLoading(false);
    }
  }, [page, status]);

  useEffect(() => { load(); }, [load]);

  // BUG FIX 3: proper cleanup of auto-refresh interval
  useEffect(() => {
    intervalRef.current = setInterval(load, 15_000);
    return () => {
      if (intervalRef.current) clearInterval(intervalRef.current);
    };
  }, [load]);

  // BUG FIX 1 & 2: retry() and cancel() now call correct endpoints
  const handleRetry = async (id: number) => {
    try {
      await apiClient.post(`/ocr/queue/${id}/retry/`);
      setToast({ type: 'success', text: 'Item queued for retry.' });
      load();
    } catch {
      setToast({ type: 'error', text: 'Retry failed.' });
    }
  };

  const handleCancel = async (id: number) => {
    try {
      await apiClient.post(`/ocr/queue/${id}/cancel/`);
      setToast({ type: 'success', text: 'Item cancelled.' });
      load();
    } catch {
      setToast({ type: 'error', text: 'Cancel failed.' });
    }
  };

  // BUG FIX 4: status change resets to page 1, not 0
  const handleStatusChange = (val: string) => {
    setStatus(val);
    setPage(1);
  };

  const totalPages = Math.ceil(total / PAGE_SIZE);

  return (
    <div className="ocr-page">
      <PageHeader title="OCR Queue" subtitle="Document OCR processing pipeline">
        <Btn size="sm" variant="ghost" onClick={load}>\u21BA Refresh</Btn>
      </PageHeader>

      <Toast msg={toast} onClose={() => setToast(null)} />

      <div className="ocr-toolbar">
        <select value={status} onChange={e => handleStatusChange(e.target.value)}>
          <option value="">All Status</option>
          {Object.entries(STATUS_LABELS).map(([v, l]) => (
            <option key={v} value={v}>{l}</option>
          ))}
        </select>
        <span className="ocr-count ocr-muted">{total} items</span>
      </div>

      <div className="ocr-table-wrap">
        <table className="ocr-table">
          <thead><tr>
            <th>Document</th>
            <th>Status</th>
            <th>Confidence</th>
            <th>Pages</th>
            <th>Queued At</th>
            <th>Actions</th>
          </tr></thead>
          <tbody>
            {loading && (
              <tr><td colSpan={6} className="ocr-center ocr-muted">Loading\u2026</td></tr>
            )}
            {!loading && items.length === 0 && (
              <tr><td colSpan={6} className="ocr-center ocr-muted">Queue is empty.</td></tr>
            )}
            {items.map(item => (
              <tr key={item.id}>
                <td className="ocr-doc-title" title={item.document_title ?? item.document}>
                  {item.document_title ?? item.document ?? `Doc #${item.document_id}`}
                </td>
                <td>
                  <span className={`ocr-badge ${STATUS_CLASS[item.status] ?? ''}`}>
                    {STATUS_LABELS[item.status] ?? item.status}
                  </span>
                </td>
                <td className="ocr-center">
                  {item.confidence_score != null
                    ? `${Math.round(item.confidence_score * 100)}%`
                    : '\u2014'
                  }
                </td>
                <td className="ocr-center">{item.total_pages ?? '\u2014'}</td>
                <td className="ocr-muted" style={{ fontSize: 11 }}>
                  {item.created_at ? new Date(item.created_at).toLocaleString('en-IN') : '\u2014'}
                </td>
                <td className="ocr-actions">
                  {item.status === 'failed' && (
                    <Btn size="sm" variant="secondary" onClick={() => handleRetry(item.id)}>
                      \u21BA Retry
                    </Btn>
                  )}
                  {(item.status === 'pending' || item.status === 'processing') && (
                    <Btn size="sm" variant="danger" onClick={() => handleCancel(item.id)}>
                      \u2715 Cancel
                    </Btn>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div className="ocr-pagination">
        <Btn size="sm" variant="secondary" disabled={page <= 1} onClick={() => setPage(p => p - 1)}>\u2190 Prev</Btn>
        <span>Page {page} / {totalPages || 1}</span>
        <Btn size="sm" variant="secondary" disabled={page >= totalPages} onClick={() => setPage(p => p + 1)}>Next \u2192</Btn>
      </div>
    </div>
  );
}

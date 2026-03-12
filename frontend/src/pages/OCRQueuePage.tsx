import { useState } from 'react';
import { useOCRQueue, useOCRQueueStats, useRetryOCR } from '../hooks/useOCR';
import type { OCRStatus } from '../api/types';

const statusBadge = (s: OCRStatus) => {
  const map: Record<OCRStatus, string> = {
    PENDING: 'pending', PROCESSING: 'processing', COMPLETED: 'completed',
    FAILED: 'failed', RETRY: 'draft', MANUAL_REVIEW: 'superseded'
  };
  return `badge badge-${map[s] ?? 'draft'}`;
};

export default function OCRQueuePage() {
  const [page, setPage] = useState(1);
  const [status, setStatus] = useState('');

  const { data, isLoading } = useOCRQueue({ page, status: status || undefined });
  const { data: stats } = useOCRQueueStats();
  const retryMut = useRetryOCR();

  return (
    <div>
      <div className="page-header">
        <div>
          <h1 className="page-title">OCR Queue</h1>
          <p className="page-subtitle">Tesseract OCR processing status for uploaded document files</p>
        </div>
      </div>

      {stats && (
        <div style={{ display: 'flex', gap: 'var(--space-3)', marginBottom: 'var(--space-5)', flexWrap: 'wrap' }}>
          {Object.entries(stats).map(([k, v]) => (
            <div key={k} className="card" style={{ padding: 'var(--space-3) var(--space-5)', minWidth: 120 }}>
              <p style={{ fontSize: 'var(--font-size-xs)', fontWeight: 600, color: 'var(--color-neutral-500)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>{k.replace(/_/g, ' ')}</p>
              <p style={{ fontSize: '1.5rem', fontWeight: 700, color: 'var(--color-neutral-900)' }}>{v}</p>
            </div>
          ))}
        </div>
      )}

      <div className="search-bar">
        <select value={status} onChange={(e) => { setStatus(e.target.value); setPage(1); }} style={{ width: 'auto' }}>
          <option value="">All Status</option>
          <option value="PENDING">Pending</option>
          <option value="PROCESSING">Processing</option>
          <option value="COMPLETED">Completed</option>
          <option value="FAILED">Failed</option>
          <option value="MANUAL_REVIEW">Manual Review</option>
        </select>
      </div>

      <div className="data-table-wrap">
        <table>
          <thead>
            <tr>
              <th>File</th>
              <th>Status</th>
              <th>Priority</th>
              <th>Attempts</th>
              <th>Engine</th>
              <th>Queued At</th>
              <th>Completed At</th>
              <th>Time (s)</th>
              <th>Action</th>
            </tr>
          </thead>
          <tbody>
            {isLoading && <tr><td colSpan={9} style={{ textAlign: 'center', padding: '2rem' }}>Loading\u2026</td></tr>}
            {(data?.results ?? []).map((item) => (
              <tr key={item.id}>
                <td style={{ maxWidth: 200, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap', fontFamily: 'var(--font-family-mono)', fontSize: 'var(--font-size-xs)' }}>{item.file_name}</td>
                <td><span className={statusBadge(item.status)}>{item.status}</span></td>
                <td>{item.priority}</td>
                <td>{item.attempts}/{item.max_attempts}</td>
                <td>{item.ocr_engine}</td>
                <td style={{ fontSize: 'var(--font-size-xs)', color: 'var(--color-neutral-500)' }}>{new Date(item.queued_at).toLocaleString('en-IN')}</td>
                <td style={{ fontSize: 'var(--font-size-xs)', color: 'var(--color-neutral-500)' }}>{item.completed_at ? new Date(item.completed_at).toLocaleString('en-IN') : '\u2014'}</td>
                <td>{item.processing_time_seconds?.toFixed(1) ?? '\u2014'}</td>
                <td>
                  {(item.status === 'FAILED' || item.status === 'MANUAL_REVIEW') && (
                    <button className="btn btn-secondary" style={{ padding: '2px 10px', fontSize: 'var(--font-size-xs)' }}
                      onClick={() => retryMut.mutate(item.id)} disabled={retryMut.isPending}>
                      Retry
                    </button>
                  )}
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

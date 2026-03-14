// =============================================================================
// FILE: frontend/src/components/pdf/PdfToolbar.tsx
// SPRINT 6 — PDF Tools toolbar for RevisionDetailPage
//
// Shows: Merge (multi-select) | Split | Rotate | Extract Pages
// Each action queues a job and polls until DONE, then offers download.
// =============================================================================
import React, { useState, useEffect } from 'react';

export interface FileAttachmentRef {
  id:        number;
  file_name: string;
  file_type: string;
}

interface Props {
  attachments:     FileAttachmentRef[];
  revisionId?:     number;
}

type Tool = 'merge' | 'split' | 'rotate' | 'extract' | null;

const POLL_INTERVAL = 2000;   // ms

async function post(url: string, body: object) {
  const res = await fetch(url, {
    method: 'POST', credentials: 'include',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  });
  return res.json();
}

async function pollJob(jobId: number): Promise<any> {
  return new Promise((resolve, reject) => {
    const timer = setInterval(async () => {
      const res = await fetch(`/api/pdf/${jobId}/`, { credentials: 'include' });
      const job = await res.json();
      if (job.status === 'DONE')   { clearInterval(timer); resolve(job); }
      if (job.status === 'FAILED') { clearInterval(timer); reject(new Error(job.error_message)); }
    }, POLL_INTERVAL);
  });
}

export const PdfToolbar: React.FC<Props> = ({ attachments, revisionId }) => {
  const [activeTool,    setActiveTool]    = useState<Tool>(null);
  const [selectedIds,   setSelectedIds]   = useState<number[]>([]);
  const [splitMode,     setSplitMode]     = useState<'ranges' | 'chunks'>('chunks');
  const [pageRanges,    setPageRanges]    = useState('1-5,6-10');  // user editable string
  const [chunkSize,     setChunkSize]     = useState(10);
  const [rotateAngle,   setRotateAngle]   = useState<90 | 180 | 270>(90);
  const [extractPages,  setExtractPages]  = useState('1,2,3');
  const [job,           setJob]           = useState<any>(null);
  const [loading,       setLoading]       = useState(false);
  const [error,         setError]         = useState<string | null>(null);

  const pdfAttachments = attachments.filter(a => a.file_type === 'PDF');
  const primaryId      = pdfAttachments[0]?.id;

  const parseRanges = (s: string) =>
    s.split(',').map(r => r.trim().split('-').map(Number)) as number[][];

  const parsePages = (s: string) =>
    s.split(',').map(p => parseInt(p.trim(), 10)).filter(Boolean);

  const runMerge = async () => {
    if (selectedIds.length < 2) { setError('Select at least 2 files to merge.'); return; }
    setLoading(true); setError(null);
    const data = await post('/api/pdf/merge/', {
      file_attachment_ids: selectedIds,
      linked_revision_id: revisionId,
    });
    await finish(data);
  };

  const runSplit = async () => {
    if (!primaryId) return;
    setLoading(true); setError(null);
    const body: any = { file_attachment_id: primaryId };
    if (splitMode === 'ranges')  body.page_ranges      = parseRanges(pageRanges);
    else                         body.pages_per_chunk  = chunkSize;
    const data = await post('/api/pdf/split/', body);
    await finish(data);
  };

  const runRotate = async () => {
    if (!primaryId) return;
    setLoading(true); setError(null);
    const data = await post('/api/pdf/rotate/', {
      file_attachment_id: primaryId,
      angle: rotateAngle,
    });
    await finish(data);
  };

  const runExtract = async () => {
    if (!primaryId) return;
    setLoading(true); setError(null);
    const data = await post('/api/pdf/extract/', {
      file_attachment_id: primaryId,
      page_numbers: parsePages(extractPages),
    });
    await finish(data);
  };

  const finish = async (jobData: any) => {
    try {
      const done = await pollJob(jobData.id);
      setJob(done);
    } catch (e: any) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  };

  const toggleSelect = (id: number) =>
    setSelectedIds(prev =>
      prev.includes(id) ? prev.filter(x => x !== id) : [...prev, id]
    );

  return (
    <div className="pdf-toolbar">
      {/* Tool selector buttons */}
      <div className="pdf-toolbar__tools">
        {(['merge', 'split', 'rotate', 'extract'] as Tool[]).map(tool => (
          <button
            key={tool!}
            className={`pdf-toolbar__btn${
              activeTool === tool ? ' pdf-toolbar__btn--active' : ''
            }`}
            onClick={() => { setActiveTool(t => t === tool ? null : tool); setJob(null); setError(null); }}
          >
            {tool === 'merge'   ? '🔗 Merge'
             : tool === 'split'   ? '✂️ Split'
             : tool === 'rotate'  ? '🔄 Rotate'
             : '📌 Extract'}
          </button>
        ))}
      </div>

      {/* ---- MERGE panel ---- */}
      {activeTool === 'merge' && (
        <div className="pdf-toolbar__panel">
          <p className="pdf-toolbar__hint">Select PDFs to merge (in order):</p>
          <ul className="pdf-toolbar__file-list">
            {pdfAttachments.map(a => (
              <li key={a.id}>
                <label>
                  <input
                    type="checkbox"
                    checked={selectedIds.includes(a.id)}
                    onChange={() => toggleSelect(a.id)}
                  />
                  {a.file_name}
                </label>
              </li>
            ))}
          </ul>
          <button className="btn btn--primary btn--sm" onClick={runMerge} disabled={loading}>
            {loading ? '⏳ Merging…' : '🔗 Merge selected'}
          </button>
        </div>
      )}

      {/* ---- SPLIT panel ---- */}
      {activeTool === 'split' && primaryId && (
        <div className="pdf-toolbar__panel">
          <label>
            <input type="radio" name="splitMode" value="chunks"
              checked={splitMode === 'chunks'}
              onChange={() => setSplitMode('chunks')} />
            {' '}Every{' '}
            <input type="number" min={1} value={chunkSize}
              onChange={e => setChunkSize(Number(e.target.value))}
              className="pdf-toolbar__num-input" />
            {' '}pages
          </label>
          <label>
            <input type="radio" name="splitMode" value="ranges"
              checked={splitMode === 'ranges'}
              onChange={() => setSplitMode('ranges')} />
            {' '}Custom ranges (e.g. <code>1-5,6-10,11-20</code>)
            {splitMode === 'ranges' && (
              <input type="text" value={pageRanges}
                onChange={e => setPageRanges(e.target.value)}
                className="pdf-toolbar__text-input" />
            )}
          </label>
          <button className="btn btn--primary btn--sm" onClick={runSplit} disabled={loading}>
            {loading ? '⏳ Splitting…' : '✂️ Split'}
          </button>
        </div>
      )}

      {/* ---- ROTATE panel ---- */}
      {activeTool === 'rotate' && primaryId && (
        <div className="pdf-toolbar__panel">
          <label>Rotate by:
            <select value={rotateAngle}
              onChange={e => setRotateAngle(Number(e.target.value) as 90 | 180 | 270)}
              className="pdf-toolbar__select">
              <option value={90}>90°</option>
              <option value={180}>180°</option>
              <option value={270}>270°</option>
            </select>
          </label>
          <button className="btn btn--primary btn--sm" onClick={runRotate} disabled={loading}>
            {loading ? '⏳…' : '🔄 Rotate all pages'}
          </button>
        </div>
      )}

      {/* ---- EXTRACT panel ---- */}
      {activeTool === 'extract' && primaryId && (
        <div className="pdf-toolbar__panel">
          <label>Page numbers (comma-separated):
            <input type="text" value={extractPages}
              onChange={e => setExtractPages(e.target.value)}
              className="pdf-toolbar__text-input"
              placeholder="e.g. 1,3,5,7" />
          </label>
          <button className="btn btn--primary btn--sm" onClick={runExtract} disabled={loading}>
            {loading ? '⏳…' : '📌 Extract'}
          </button>
        </div>
      )}

      {/* Error + Download */}
      {error && <p className="pdf-toolbar__error">{error}</p>}
      {job?.status === 'DONE' && (
        <div className="pdf-toolbar__downloads">
          <strong>✅ Done! Download output{job.output_files.length > 1 ? 's' : ''}:</strong>
          <ul>
            {job.output_files.map((_: string, idx: number) => (
              <li key={idx}>
                <a
                  href={`/api/pdf/${job.id}/download/${idx}/`}
                  download
                  className="btn btn--link btn--sm"
                >
                  ⬇️ Part {idx + 1}
                </a>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
};

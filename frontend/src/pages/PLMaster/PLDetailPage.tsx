// =============================================================================
// FILE: frontend/src/pages/PLMaster/PLDetailPage.tsx
// PL DETAIL PAGE — shows PL info + Technical Evaluation Documents panel
//
// Technical Evaluation Documents section:
//   — Stores up to 3 evaluation documents per PL (per tender reference)
//   — Accepts PDF and DOCX formats only
//   — Each slot shows: Tender No., Eval Year, uploaded file, download + delete
//   — Serves as reference for the next technical evaluation case
//   — Backend: POST /pl-master/{pl_number}/tech-eval-docs/
//              GET  /pl-master/{pl_number}/tech-eval-docs/
//              DELETE /pl-master/{pl_number}/tech-eval-docs/{id}/
// =============================================================================
import React, { useEffect, useRef, useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { plMasterService } from '../../services/plMasterService';

// ─── Types ───────────────────────────────────────────────────────────────────
interface TechEvalDoc {
  id          : number;
  tender_number: string;
  eval_year   : number | string;
  file_name   : string;
  file_format : 'PDF' | 'DOCX';
  file_size_kb: number;
  uploaded_by : string;
  uploaded_at : string;
  download_url: string;
}

type UploadSlot = {
  tender_number: string;
  eval_year    : string;
  file         : File | null;
};

// ─── Styles (inline — no extra CSS file needed) ───────────────────────────────
const S = {
  page    : { padding: 24, maxWidth: 960 } as React.CSSProperties,
  card    : { background: '#151b2e', border: '1.5px solid #2d3555', borderRadius: 12, marginBottom: 24, overflow: 'hidden' } as React.CSSProperties,
  cardHead: { padding: '12px 20px', background: '#1a2238', borderBottom: '1px solid #2d3555', display: 'flex', justifyContent: 'space-between', alignItems: 'center' } as React.CSSProperties,
  cardTitle:{ color: '#4b6cb7', fontWeight: 700, fontSize: 13, letterSpacing: '0.06em', textTransform: 'uppercase' } as React.CSSProperties,
  cardBody: { padding: 20 } as React.CSSProperties,
  row     : { display: 'flex', gap: 12, alignItems: 'center', padding: '10px 0', borderBottom: '1px solid #1e2a3e' } as React.CSSProperties,
  label   : { color: '#94a3b8', fontSize: 11, fontWeight: 700, minWidth: 120, textTransform: 'uppercase', letterSpacing: '0.05em' } as React.CSSProperties,
  value   : { color: '#d1d5db', fontSize: 13, flex: 1 } as React.CSSProperties,
  badge   : (color: string): React.CSSProperties => ({ padding: '2px 8px', borderRadius: 4, fontSize: 11, fontWeight: 700, background: color + '22', color }),
  btn     : (bg?: string): React.CSSProperties => ({ padding: '6px 14px', background: bg ?? '#1e2332', border: '1px solid #2d3555', color: bg ? '#fff' : '#d1d5db', borderRadius: 6, fontSize: 12, fontWeight: 600, cursor: 'pointer', whiteSpace: 'nowrap' as const }),
  input   : { padding: '6px 10px', background: '#1e2332', border: '1px solid #2d3555', color: '#d1d5db', borderRadius: 6, fontSize: 12, width: '100%' } as React.CSSProperties,
  alert   : (t: 'ok'|'err'): React.CSSProperties => ({ padding: '10px 16px', borderRadius: 8, fontSize: 13, fontWeight: 500, marginBottom: 14, background: t==='ok' ? '#14532d' : '#7f1d1d', color: t==='ok' ? '#86efac' : '#fca5a5' }),
  docRow  : { display: 'flex', gap: 10, alignItems: 'center', padding: '10px 16px', borderBottom: '1px solid #1e2a3e', flexWrap: 'wrap' as const } as React.CSSProperties,
  emptyHint: { color: '#4b5563', fontSize: 13, padding: '20px 0', textAlign: 'center' as const } as React.CSSProperties,
};

// ─── Main page ────────────────────────────────────────────────────────────────
export default function PLDetailPage() {
  const { plNumber }  = useParams<{ plNumber: string }>();
  const navigate      = useNavigate();
  const [pl, setPl]   = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error,   setError]   = useState('');

  useEffect(() => {
    if (!plNumber) return;
    plMasterService.getPL(plNumber)
      .then(setPl)
      .catch(() => setError('PL item not found.'))
      .finally(() => setLoading(false));
  }, [plNumber]);

  if (loading) return <div style={{ padding: 32, color: '#94a3b8' }}>Loading PL details…</div>;
  if (error)   return <div style={{ padding: 32, color: '#f87171' }}>❌ {error}</div>;
  if (!pl)     return null;

  return (
    <div style={S.page}>
      {/* Back nav */}
      <button onClick={() => navigate('/pl-master')} style={{ ...S.btn(), marginBottom: 20 }}>
        ← Back to PL Master
      </button>

      {/* ── PL Info Card ──────────────────────────────────────────────── */}
      <div style={S.card}>
        <div style={S.cardHead}>
          <span style={S.cardTitle}>PL Details — {pl.pl_number}</span>
          <button onClick={() => navigate(`/pl-master/${pl.pl_number}/edit`)} style={S.btn()}>✏️ Edit</button>
        </div>
        <div style={S.cardBody}>
          {[
            ['PL Number',          pl.pl_number],
            ['Description',        pl.description ?? '—'],
            ['UVAM ID',            pl.uvam_id ?? '—'],
            ['Inspection Category',pl.inspection_category ?? '—'],
            ['Safety Item',        pl.safety_item ? '✅ Yes' : '❌ No'],
            ['Loco Types',         (pl.loco_types ?? []).join(', ') || '—'],
            ['Application Area',   pl.application_area ?? '—'],
            ['Used In',            pl.used_in ?? '—'],
          ].map(([label, val]) => (
            <div key={label as string} style={S.row}>
              <span style={S.label}>{label}</span>
              <span style={S.value}>{val as string}</span>
            </div>
          ))}
        </div>
      </div>

      {/* ── Technical Evaluation Documents ───────────────────────────── */}
      <TechEvalDocsPanel plNumber={pl.pl_number} />
    </div>
  );
}

// =============================================================================
// TECHNICAL EVALUATION DOCUMENTS PANEL
// =============================================================================
function TechEvalDocsPanel({ plNumber }: { plNumber: string }) {
  const MAX_DOCS = 3;

  const [docs,    setDocs]    = useState<TechEvalDoc[]>([]);
  const [loading, setLoading] = useState(true);
  const [msg,     setMsg]     = useState<{ type: 'ok'|'err'; text: string } | null>(null);
  const [uploading, setUploading] = useState(false);
  const [showForm,  setShowForm]  = useState(false);
  const [slot, setSlot] = useState<UploadSlot>({
    tender_number: '', eval_year: String(new Date().getFullYear()), file: null,
  });
  const fileRef = useRef<HTMLInputElement>(null);

  const showMsg = (type: 'ok'|'err', text: string) => {
    setMsg({ type, text });
    setTimeout(() => setMsg(null), 4000);
  };

  // Load existing docs
  const loadDocs = () => {
    setLoading(true);
    plMasterService.listTechEvalDocs(plNumber)
      .then(data => setDocs(data.results ?? data))
      .catch(() => showMsg('err', 'Could not load evaluation documents.'))
      .finally(() => setLoading(false));
  };

  useEffect(() => { loadDocs(); }, [plNumber]);

  // Upload
  const handleUpload = async () => {
    if (!slot.tender_number.trim()) { showMsg('err', 'Tender number is required.'); return; }
    if (!slot.eval_year)            { showMsg('err', 'Evaluation year is required.'); return; }
    if (!slot.file)                 { showMsg('err', 'Please select a file.'); return; }
    if (docs.length >= MAX_DOCS)    { showMsg('err', `Maximum ${MAX_DOCS} evaluation documents allowed. Delete one first.`); return; }

    const ext = slot.file.name.split('.').pop()?.toLowerCase() ?? '';
    if (!['pdf', 'docx'].includes(ext)) {
      showMsg('err', 'Only PDF and DOCX files are accepted.');
      return;
    }
    if (slot.file.size > 20 * 1024 * 1024) {
      showMsg('err', 'File size must be under 20 MB.');
      return;
    }

    setUploading(true);
    try {
      await plMasterService.uploadTechEvalDoc(plNumber, {
        tender_number: slot.tender_number.trim(),
        eval_year    : slot.eval_year,
        file         : slot.file,
      });
      showMsg('ok', `Document uploaded — ${slot.file.name}`);
      setSlot({ tender_number: '', eval_year: String(new Date().getFullYear()), file: null });
      if (fileRef.current) fileRef.current.value = '';
      setShowForm(false);
      loadDocs();
    } catch (e: any) {
      showMsg('err', e?.detail ?? e?.message ?? 'Upload failed.');
    } finally {
      setUploading(false);
    }
  };

  // Delete
  const handleDelete = async (doc: TechEvalDoc) => {
    if (!window.confirm(`Delete "${doc.file_name}"? This cannot be undone.`)) return;
    try {
      await plMasterService.deleteTechEvalDoc(plNumber, doc.id);
      showMsg('ok', 'Document removed.');
      loadDocs();
    } catch {
      showMsg('err', 'Delete failed.');
    }
  };

  const fmtSize = (kb: number) =>
    kb >= 1024 ? `${(kb / 1024).toFixed(1)} MB` : `${kb} KB`;

  const fmtDate = (iso: string) =>
    new Date(iso).toLocaleDateString('en-IN', { day:'2-digit', month:'short', year:'numeric' });

  return (
    <div style={S.card}>
      {/* Header */}
      <div style={S.cardHead}>
        <div>
          <span style={S.cardTitle}>📄 Technical Evaluation Documents</span>
          <span style={{ color: '#4b5563', fontSize: 11, marginLeft: 12 }}>
            Last {MAX_DOCS} tender evaluation documents for reference &nbsp;&bull;&nbsp;
            {docs.length} / {MAX_DOCS} uploaded
          </span>
        </div>
        {docs.length < MAX_DOCS && (
          <button
            style={S.btn('linear-gradient(135deg,#4b6cb7,#182848)')}
            onClick={() => setShowForm(s => !s)}
          >
            {showForm ? '✕ Cancel' : '⬆ Attach Document'}
          </button>
        )}
      </div>

      <div style={S.cardBody}>
        {/* Alert */}
        {msg && <div style={S.alert(msg.type)}>{msg.type === 'ok' ? '✅' : '❌'} {msg.text}</div>}

        {/* Upload Form */}
        {showForm && (
          <div style={{
            background: '#1a2238', border: '1px solid #2d3555', borderRadius: 10,
            padding: 18, marginBottom: 20,
          }}>
            <div style={{ color: '#94a3b8', fontSize: 12, fontWeight: 700, marginBottom: 14,
              textTransform: 'uppercase', letterSpacing: '0.06em' }}>
              Upload Evaluation Document
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px 20px', marginBottom: 14 }}>
              {/* Tender Number */}
              <div>
                <label style={{ ...S.label, display: 'block', marginBottom: 5 }}>Tender Number *</label>
                <input
                  style={S.input}
                  placeholder="e.g. TEN/EL/2023-24/001"
                  value={slot.tender_number}
                  onChange={e => setSlot(s => ({ ...s, tender_number: e.target.value }))}
                />
              </div>

              {/* Evaluation Year */}
              <div>
                <label style={{ ...S.label, display: 'block', marginBottom: 5 }}>Evaluation Year *</label>
                <input
                  type="number"
                  style={S.input}
                  min={2000}
                  max={2099}
                  value={slot.eval_year}
                  onChange={e => setSlot(s => ({ ...s, eval_year: e.target.value }))}
                />
              </div>

              {/* File picker — full width */}
              <div style={{ gridColumn: '1 / -1' }}>
                <label style={{ ...S.label, display: 'block', marginBottom: 5 }}>
                  Select File * &nbsp;
                  <span style={{ color: '#4b5563', fontWeight: 400, textTransform: 'none', fontSize: 11 }}>
                    (PDF or DOCX only, max 20 MB)
                  </span>
                </label>
                <input
                  ref={fileRef}
                  type="file"
                  accept=".pdf,.docx,application/pdf,application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                  style={{ ...S.input, padding: '5px 8px', cursor: 'pointer' }}
                  onChange={e => setSlot(s => ({ ...s, file: e.target.files?.[0] ?? null }))}
                />
                {slot.file && (
                  <div style={{ color: '#60a5fa', fontSize: 12, marginTop: 6 }}>
                    📎 {slot.file.name} ({fmtSize(Math.round(slot.file.size / 1024))})
                  </div>
                )}
              </div>
            </div>

            <div style={{ display: 'flex', gap: 10 }}>
              <button
                style={S.btn('linear-gradient(135deg,#4b6cb7,#182848)')}
                onClick={handleUpload}
                disabled={uploading}
              >
                {uploading ? '⏳ Uploading…' : '💾 Upload & Attach'}
              </button>
              <button style={S.btn()} onClick={() => setShowForm(false)}>Cancel</button>
            </div>
          </div>
        )}

        {/* Document List */}
        {loading ? (
          <p style={{ color: '#94a3b8', fontSize: 13 }}>Loading documents…</p>
        ) : docs.length === 0 ? (
          <div style={S.emptyHint}>
            <div style={{ fontSize: 28, marginBottom: 8 }}>📂</div>
            No technical evaluation documents attached yet.<br />
            <span style={{ fontSize: 11 }}>Attach up to {MAX_DOCS} PDF or DOCX evaluation documents for reference.</span>
          </div>
        ) : (
          docs.map((doc, idx) => (
            <div key={doc.id} style={S.docRow}>
              {/* Slot number */}
              <span style={{
                width: 28, height: 28, borderRadius: '50%',
                background: '#1e2b45', color: '#60a5fa',
                display: 'flex', alignItems: 'center', justifyContent: 'center',
                fontWeight: 700, fontSize: 12, flexShrink: 0,
              }}>{idx + 1}</span>

              {/* Format badge */}
              <span style={S.badge(doc.file_format === 'PDF' ? '#ef4444' : '#3b82f6')}>
                {doc.file_format}
              </span>

              {/* File info */}
              <div style={{ flex: 1, minWidth: 0 }}>
                <div style={{ color: '#d1d5db', fontSize: 13, fontWeight: 600,
                  overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                  {doc.file_name}
                </div>
                <div style={{ color: '#6b7280', fontSize: 11, marginTop: 2 }}>
                  Tender: <span style={{ color: '#94a3b8' }}>{doc.tender_number}</span>
                  &nbsp;•&nbsp;
                  Year: <span style={{ color: '#94a3b8' }}>{doc.eval_year}</span>
                  &nbsp;•&nbsp;
                  {fmtSize(doc.file_size_kb)}
                  &nbsp;•&nbsp;
                  Uploaded {fmtDate(doc.uploaded_at)} by {doc.uploaded_by}
                </div>
              </div>

              {/* Actions */}
              <a
                href={doc.download_url}
                download={doc.file_name}
                target="_blank"
                rel="noreferrer"
                style={{ ...S.btn(), textDecoration: 'none', display: 'inline-flex', alignItems: 'center', gap: 4 }}
              >
                ⬇ Download
              </a>
              <button
                style={S.btn()}
                onClick={() => handleDelete(doc)}
                title="Remove this document"
              >
                🗑️ Remove
              </button>
            </div>
          ))
        )}

        {/* Slot indicator */}
        {!loading && docs.length > 0 && docs.length < MAX_DOCS && (
          <div style={{ color: '#4b5563', fontSize: 11, marginTop: 12, textAlign: 'center' }}>
            {MAX_DOCS - docs.length} slot{MAX_DOCS - docs.length > 1 ? 's' : ''} remaining
          </div>
        )}
        {!loading && docs.length >= MAX_DOCS && (
          <div style={{ color: '#f59e0b', fontSize: 11, marginTop: 12, textAlign: 'center' }}>
            ⚠️ Maximum {MAX_DOCS} documents stored. Remove an old one to attach a newer evaluation.
          </div>
        )}
      </div>
    </div>
  );
}

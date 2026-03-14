// =============================================================================
// FILE: frontend/src/pages/PLMaster/PLDetailPage.tsx
// PL DETAIL PAGE — full redesign
//
// Sections:
//   A. PL Info card
//   B. VD / NVD Vendor Info (toggle + save inline)
//   C. Documents Side Panel  (accordion: 6 categories + tech-eval)
//        — search bar filters across all linked docs
//        — each category accordion shows its docs
//        — Link Document: search EDMS docs, pick category, link
//        — Unlink / Open Preview
//   D. Technical Evaluation Documents (upload panel, max 3)
// =============================================================================
import React, { useEffect, useRef, useState, useCallback } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { plMasterService } from '../../services/plMasterService';

// ── Types ─────────────────────────────────────────────────────────────────────
interface LinkedDoc {
  id             : number;
  document_id    : number | null;
  document_title : string;
  document_number: string;
  category       : string;
  category_label : string;
  remarks        : string;
  linked_by_name : string;
  linked_at      : string;
}

interface TechEvalDoc {
  id           : number;
  tender_number: string;
  eval_year    : number | string;
  file_name    : string;
  file_format  : 'PDF' | 'DOCX';
  file_size_kb : number;
  uploaded_by  : string;
  uploaded_at  : string;
  download_url : string;
}

interface VendorInfo {
  vendor_type          : 'VD' | 'NVD';
  uvam_vd_number       : string;
  eligibility_criteria : string;
  word_count          ?: number;
  updated_by_name     ?: string;
  updated_at          ?: string;
}

const CATEGORIES = [
  { key: 'SPECIFICATION', label: 'Specifications',                  icon: '📋' },
  { key: 'DRAWING',       label: 'Drawings',                        icon: '📐' },
  { key: 'STANDARD',      label: 'Standards',                       icon: '📏' },
  { key: 'STR',           label: 'STR — Special Technical Req.',    icon: '📌' },
  { key: 'TECH_EVAL',     label: 'Technical Evaluation Documents',  icon: '📊' },
  { key: 'OTHER',         label: 'Other Technical Documents',       icon: '📎' },
];

// ── Styles ────────────────────────────────────────────────────────────────────
const S = {
  page       : { display:'flex', gap:24, padding:24, maxWidth:1400, alignItems:'flex-start' } as React.CSSProperties,
  main       : { flex:1, minWidth:0 } as React.CSSProperties,
  side       : { width:440, flexShrink:0 } as React.CSSProperties,
  card       : { background:'#151b2e', border:'1.5px solid #2d3555', borderRadius:12, marginBottom:20, overflow:'hidden' } as React.CSSProperties,
  cardHead   : { padding:'11px 18px', background:'#1a2238', borderBottom:'1px solid #2d3555', display:'flex', justifyContent:'space-between', alignItems:'center' } as React.CSSProperties,
  cardTitle  : { color:'#4b6cb7', fontWeight:700, fontSize:12, letterSpacing:'0.07em', textTransform:'uppercase' as const },
  cardBody   : { padding:18 } as React.CSSProperties,
  row        : { display:'flex', gap:10, alignItems:'flex-start', padding:'8px 0', borderBottom:'1px solid #1e2a3e' } as React.CSSProperties,
  label      : { color:'#94a3b8', fontSize:11, fontWeight:700, minWidth:130, textTransform:'uppercase' as const, letterSpacing:'0.05em', paddingTop:1 },
  value      : { color:'#d1d5db', fontSize:13, flex:1 } as React.CSSProperties,
  btn        : (bg?:string, sm?:boolean): React.CSSProperties => ({ padding: sm ? '4px 10px' : '7px 15px', background:bg??'#1e2332', border:'1px solid #2d3555', color: bg ? '#fff':'#d1d5db', borderRadius:6, fontSize: sm?11:12, fontWeight:600, cursor:'pointer', whiteSpace:'nowrap' as const }),
  input      : { padding:'6px 10px', background:'#1e2332', border:'1px solid #2d3555', color:'#d1d5db', borderRadius:6, fontSize:12, width:'100%', boxSizing:'border-box' as const } as React.CSSProperties,
  textarea   : { padding:'8px 10px', background:'#1e2332', border:'1px solid #2d3555', color:'#d1d5db', borderRadius:6, fontSize:12, width:'100%', boxSizing:'border-box' as const, resize:'vertical' as const, minHeight:100 } as React.CSSProperties,
  alert      : (t:'ok'|'err'|'warn'): React.CSSProperties => ({ padding:'9px 14px', borderRadius:7, fontSize:12, fontWeight:500, marginBottom:12, background: t==='ok'?'#14532d': t==='err'?'#7f1d1d':'#431407', color: t==='ok'?'#86efac': t==='err'?'#fca5a5':'#fdba74' }),
  badge      : (c:string): React.CSSProperties => ({ padding:'2px 7px', borderRadius:4, fontSize:10, fontWeight:700, background:c+'22', color:c, display:'inline-block' }),
  accordion  : { marginBottom:8, border:'1px solid #222d44', borderRadius:8, overflow:'hidden' } as React.CSSProperties,
  accHead    : (open:boolean): React.CSSProperties => ({ padding:'9px 14px', background: open?'#1e2b45':'#181e30', cursor:'pointer', display:'flex', justifyContent:'space-between', alignItems:'center', userSelect:'none' as const }),
  accBody    : { padding:'8px 12px 12px' } as React.CSSProperties,
  docItem    : { display:'flex', gap:8, alignItems:'center', padding:'6px 8px', borderRadius:6, background:'#1e2332', marginBottom:6 } as React.CSSProperties,
  searchBox  : { padding:'7px 10px', background:'#1a2238', border:'1px solid #2d3555', color:'#d1d5db', borderRadius:7, fontSize:12, width:'100%', boxSizing:'border-box' as const } as React.CSSProperties,
};

// ── Main page ─────────────────────────────────────────────────────────────────
export default function PLDetailPage() {
  const { plNumber } = useParams<{ plNumber: string }>();
  const navigate     = useNavigate();
  const [pl,      setPl]     = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error,   setError]   = useState('');

  useEffect(() => {
    if (!plNumber) return;
    plMasterService.getPL(plNumber)
      .then(setPl)
      .catch(() => setError('PL item not found.'))
      .finally(() => setLoading(false));
  }, [plNumber]);

  if (loading) return <div style={{padding:32,color:'#94a3b8'}}>Loading PL details…</div>;
  if (error)   return <div style={{padding:32,color:'#f87171'}}>❌ {error}</div>;
  if (!pl)     return null;

  return (
    <div>
      <div style={{padding:'16px 24px 0'}}>
        <button onClick={() => navigate('/pl-master')} style={S.btn()}>
          ← Back to PL Master
        </button>
      </div>
      <div style={S.page}>
        {/* ── LEFT MAIN ────────────────────────────────────────────────── */}
        <div style={S.main}>
          <PLInfoCard pl={pl} />
          <VendorInfoCard plNumber={pl.pl_number} />
          <TechEvalDocsPanel plNumber={pl.pl_number} />
        </div>
        {/* ── RIGHT SIDE PANEL ─────────────────────────────────────────── */}
        <div style={S.side}>
          <LinkedDocsPanel plNumber={pl.pl_number} />
        </div>
      </div>
    </div>
  );
}

// ── PL Info Card ─────────────────────────────────────────────────────────────
function PLInfoCard({ pl }: { pl: any }) {
  const navigate = useNavigate();
  return (
    <div style={S.card}>
      <div style={S.cardHead}>
        <span style={S.cardTitle}>PL Details — {pl.pl_number}</span>
        <button onClick={() => navigate(`/pl-master/${pl.pl_number}/edit`)} style={S.btn()}>✏️ Edit</button>
      </div>
      <div style={S.cardBody}>
        {([
          ['PL Number',          pl.pl_number],
          ['Description',        pl.description ?? '—'],
          ['UVAM ID',            pl.uvam_id ?? '—'],
          ['Inspection Category',pl.inspection_category ?? '—'],
          ['Safety Item',        pl.safety_item ? '✅ Yes' : '❌ No'],
          ['Loco Types',         (pl.loco_types ?? []).join(', ') || '—'],
          ['Application Area',   pl.application_area ?? '—'],
        ] as [string,string][]).map(([label, val]) => (
          <div key={label} style={S.row}>
            <span style={S.label}>{label}</span>
            <span style={S.value}>{val}</span>
          </div>
        ))}
      </div>
    </div>
  );
}

// ── VD / NVD Vendor Info Card ─────────────────────────────────────────────────
function VendorInfoCard({ plNumber }: { plNumber: string }) {
  const [info,    setInfo]    = useState<VendorInfo|null>(null);
  const [editing, setEditing] = useState(false);
  const [draft,   setDraft]   = useState<VendorInfo>({ vendor_type:'NVD', uvam_vd_number:'', eligibility_criteria:'' });
  const [saving,  setSaving]  = useState(false);
  const [msg,     setMsg]     = useState<{t:'ok'|'err';s:string}|null>(null);

  useEffect(() => {
    plMasterService.getVendorInfo(plNumber).then(d => { setInfo(d); setDraft(d); });
  }, [plNumber]);

  const wordCount = (draft.eligibility_criteria ?? '').trim() === ''
    ? 0 : draft.eligibility_criteria.trim().split(/\s+/).length;

  const save = async () => {
    if (draft.vendor_type === 'VD' && !draft.uvam_vd_number.trim()) {
      setMsg({ t:'err', s:'UVAM VD Number is required.' }); return;
    }
    if (draft.vendor_type === 'NVD' && wordCount > 2000) {
      setMsg({ t:'err', s:`Eligibility criteria exceeds 2000 words (${wordCount}).` }); return;
    }
    setSaving(true);
    try {
      const updated = await plMasterService.saveVendorInfo(plNumber, draft);
      setInfo(updated); setEditing(false);
      setMsg({ t:'ok', s:'Vendor info saved.' });
      setTimeout(() => setMsg(null), 3000);
    } catch (e: any) {
      setMsg({ t:'err', s: e?.detail ?? 'Save failed.' });
    } finally { setSaving(false); }
  };

  const VD_COLOR  = '#22c55e';
  const NVD_COLOR = '#f59e0b';

  return (
    <div style={S.card}>
      <div style={S.cardHead}>
        <div style={{display:'flex',gap:10,alignItems:'center'}}>
          <span style={S.cardTitle}>Vendor / Eligibility</span>
          {info && (
            <span style={S.badge(info.vendor_type === 'VD' ? VD_COLOR : NVD_COLOR)}>
              {info.vendor_type === 'VD' ? '✅ VD' : '⚠ NVD'}
            </span>
          )}
        </div>
        <button style={S.btn()} onClick={() => setEditing(e => !e)}>
          {editing ? '✕ Cancel' : '✏️ Edit'}
        </button>
      </div>
      <div style={S.cardBody}>
        {msg && <div style={S.alert(msg.t)}>{msg.s}</div>}

        {!editing ? (
          // READ VIEW
          info ? (
            <div>
              <div style={S.row}>
                <span style={S.label}>Type</span>
                <span style={S.value}>
                  <span style={S.badge(info.vendor_type==='VD'?VD_COLOR:NVD_COLOR)}>
                    {info.vendor_type === 'VD' ? 'VD — Vendor Directory' : 'NVD — Non-Vendor Directory'}
                  </span>
                </span>
              </div>
              {info.vendor_type === 'VD' && (
                <div style={S.row}>
                  <span style={S.label}>UVAM VD No.</span>
                  <span style={{...S.value, fontFamily:'monospace', color:'#60a5fa'}}>{info.uvam_vd_number || '—'}</span>
                </div>
              )}
              {info.vendor_type === 'NVD' && (
                <div style={S.row}>
                  <span style={S.label}>Eligibility</span>
                  <span style={{...S.value, whiteSpace:'pre-wrap', fontSize:12, lineHeight:1.6}}>
                    {info.eligibility_criteria || '—'}
                    {info.eligibility_criteria && (
                      <span style={{color:'#4b5563',fontSize:10,marginLeft:8}}>
                        ({info.word_count ?? wordCount} words)
                      </span>
                    )}
                  </span>
                </div>
              )}
              {info.updated_at && (
                <div style={{color:'#4b5563',fontSize:10,marginTop:8}}>
                  Last updated {new Date(info.updated_at).toLocaleDateString('en-IN')} by {info.updated_by_name || 'System'}
                </div>
              )}
            </div>
          ) : <p style={{color:'#4b5563',fontSize:13}}>Loading…</p>
        ) : (
          // EDIT VIEW
          <div>
            {/* Toggle VD / NVD */}
            <div style={{display:'flex',gap:8,marginBottom:16}}>
              {(['VD','NVD'] as const).map(t => (
                <button
                  key={t}
                  onClick={() => setDraft(d => ({...d, vendor_type:t}))}
                  style={{
                    ...S.btn(draft.vendor_type===t ? (t==='VD'?'#166534':'#92400e') : undefined),
                    flex:1, fontWeight: draft.vendor_type===t ? 700 : 400,
                    border: draft.vendor_type===t ? `2px solid ${t==='VD'?VD_COLOR:NVD_COLOR}` : '1px solid #2d3555',
                  }}
                >
                  {t === 'VD' ? '✅ VD — Vendor Directory' : '⚠ NVD — Non-Vendor Directory'}
                </button>
              ))}
            </div>

            {draft.vendor_type === 'VD' ? (
              <div style={{marginBottom:14}}>
                <label style={{...S.label,display:'block',marginBottom:5}}>UVAM Vendor Directory Number *</label>
                <input
                  style={S.input}
                  placeholder="e.g. VD/EL/WAG9/0042"
                  value={draft.uvam_vd_number}
                  onChange={e => setDraft(d => ({...d, uvam_vd_number:e.target.value}))}
                />
              </div>
            ) : (
              <div style={{marginBottom:14}}>
                <label style={{...S.label,display:'block',marginBottom:5}}>
                  Eligibility Criteria *
                  <span style={{color: wordCount>1800?'#f87171':'#4b5563', fontWeight:400, marginLeft:8, textTransform:'none' as const}}>
                    {wordCount} / 2000 words
                  </span>
                </label>
                <textarea
                  style={S.textarea}
                  rows={8}
                  placeholder="Describe eligibility criteria for vendor selection (max 2000 words)…"
                  value={draft.eligibility_criteria}
                  onChange={e => setDraft(d => ({...d, eligibility_criteria:e.target.value}))}
                />
              </div>
            )}

            <div style={{display:'flex',gap:8}}>
              <button style={S.btn('linear-gradient(135deg,#4b6cb7,#182848)')} onClick={save} disabled={saving}>
                {saving ? '⏳ Saving…' : '💾 Save'}
              </button>
              <button style={S.btn()} onClick={() => { setEditing(false); setDraft(info ?? draft); }}>Cancel</button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

// ── Linked Documents Side Panel ───────────────────────────────────────────────
function LinkedDocsPanel({ plNumber }: { plNumber: string }) {
  const navigate = useNavigate();
  const [grouped,    setGrouped]    = useState<Record<string,LinkedDoc[]>>({});
  const [total,      setTotal]      = useState(0);
  const [loading,    setLoading]    = useState(true);
  const [search,     setSearch]     = useState('');
  const [openCats,   setOpenCats]   = useState<Set<string>>(new Set(CATEGORIES.map(c=>c.key)));
  const [msg,        setMsg]        = useState<{t:'ok'|'err';s:string}|null>(null);
  const [showLink,   setShowLink]   = useState(false);
  // Link form state
  const [linkSearch, setLinkSearch] = useState('');
  const [linkResults,setLinkResults]= useState<any[]>([]);
  const [linkCat,    setLinkCat]    = useState('OTHER');
  const [linkRemarks,setLinkRemarks]= useState('');
  const [linking,    setLinking]    = useState(false);
  const searchTimer = useRef<ReturnType<typeof setTimeout>|null>(null);

  const showMsg = (t:'ok'|'err', s:string) => {
    setMsg({t,s}); setTimeout(()=>setMsg(null),4000);
  };

  const load = useCallback(() => {
    setLoading(true);
    plMasterService.listLinkedDocs(plNumber, search ? {q:search} : {})
      .then(data => {
        setGrouped(data.grouped ?? {});
        setTotal(data.total ?? 0);
      })
      .catch(() => showMsg('err','Failed to load linked documents.'))
      .finally(() => setLoading(false));
  }, [plNumber, search]);

  useEffect(() => { load(); }, [load]);

  // Debounced doc search for link form
  useEffect(() => {
    if (searchTimer.current) clearTimeout(searchTimer.current);
    if (linkSearch.length < 2) { setLinkResults([]); return; }
    searchTimer.current = setTimeout(() => {
      plMasterService.searchDocsToLink(plNumber, linkSearch)
        .then(d => setLinkResults(d.results ?? []));
    }, 350);
  }, [linkSearch, plNumber]);

  const toggleCat = (key: string) =>
    setOpenCats(prev => {
      const s = new Set(prev);
      s.has(key) ? s.delete(key) : s.add(key);
      return s;
    });

  const handleUnlink = async (doc: LinkedDoc) => {
    if (!window.confirm(`Unlink "${doc.document_number || doc.document_title}" from this PL?`)) return;
    try {
      await plMasterService.unlinkDocument(plNumber, doc.id);
      showMsg('ok','Document unlinked.');
      load();
    } catch { showMsg('err','Unlink failed.'); }
  };

  const handleLink = async (docResult: any) => {
    setLinking(true);
    try {
      await plMasterService.linkDocument(plNumber, {
        document_id    : docResult.id,
        document_title : docResult.title,
        document_number: docResult.document_number,
        category       : linkCat,
        remarks        : linkRemarks,
      });
      showMsg('ok',`Linked: ${docResult.document_number}`);
      setShowLink(false); setLinkSearch(''); setLinkResults([]);
      load();
    } catch (e:any) {
      showMsg('err', e?.detail ?? 'Link failed.');
    } finally { setLinking(false); }
  };

  const fmtDate = (iso: string) =>
    new Date(iso).toLocaleDateString('en-IN',{day:'2-digit',month:'short',year:'numeric'});

  const CAT_COLORS: Record<string,string> = {
    SPECIFICATION:'#3b82f6', DRAWING:'#8b5cf6', STANDARD:'#14b8a6',
    STR:'#f59e0b', TECH_EVAL:'#22c55e', OTHER:'#6b7280',
  };

  return (
    <div style={S.card}>
      <div style={S.cardHead}>
        <div>
          <span style={S.cardTitle}>📂 Linked Documents</span>
          <span style={{color:'#4b5563',fontSize:11,marginLeft:8}}>{total} / 100</span>
        </div>
        {total < 100 && (
          <button style={S.btn('linear-gradient(135deg,#4b6cb7,#182848)',true)}
            onClick={() => setShowLink(s=>!s)}>
            {showLink ? '✕ Close' : '+ Link Doc'}
          </button>
        )}
      </div>
      <div style={S.cardBody}>
        {msg && <div style={S.alert(msg.t)}>{msg.s}</div>}

        {/* Global search */}
        <input
          style={{...S.searchBox, marginBottom:12}}
          placeholder="🔍 Search linked documents…"
          value={search}
          onChange={e => setSearch(e.target.value)}
        />

        {/* Link Form */}
        {showLink && (
          <div style={{background:'#1a2238',border:'1px solid #2d3555',borderRadius:8,padding:14,marginBottom:14}}>
            <div style={{color:'#94a3b8',fontSize:11,fontWeight:700,marginBottom:10,textTransform:'uppercase',letterSpacing:'0.06em'}}>Link Document to PL</div>

            {/* Category selector */}
            <div style={{marginBottom:10}}>
              <label style={{...S.label,display:'block',marginBottom:4}}>Category</label>
              <select
                style={{...S.input,cursor:'pointer'}}
                value={linkCat}
                onChange={e => setLinkCat(e.target.value)}
              >
                {CATEGORIES.map(c => <option key={c.key} value={c.key}>{c.icon} {c.label}</option>)}
              </select>
            </div>

            {/* Doc search */}
            <div style={{marginBottom:10}}>
              <label style={{...S.label,display:'block',marginBottom:4}}>Search EDMS Document</label>
              <input
                style={S.input}
                placeholder="Type document number or title (min 2 chars)…"
                value={linkSearch}
                onChange={e => setLinkSearch(e.target.value)}
              />
            </div>

            {/* Results */}
            {linkResults.length > 0 && (
              <div style={{maxHeight:200,overflowY:'auto',marginBottom:10}}>
                {linkResults.map(doc => (
                  <div key={doc.id} style={{
                    ...S.docItem,
                    cursor:'pointer',
                    flexDirection:'column',
                    alignItems:'flex-start',
                  }}
                    onMouseEnter={e => (e.currentTarget.style.background='#2d3a55')}
                    onMouseLeave={e => (e.currentTarget.style.background='#1e2332')}
                  >
                    <div style={{display:'flex',justifyContent:'space-between',width:'100%',gap:6}}>
                      <div>
                        <span style={{color:'#60a5fa',fontSize:11,fontFamily:'monospace'}}>{doc.document_number}</span>
                        <span style={{color:'#d1d5db',fontSize:12,marginLeft:8}}>{doc.title}</span>
                      </div>
                      <button
                        style={S.btn('linear-gradient(135deg,#065f46,#064e3b)',true)}
                        onClick={() => handleLink(doc)}
                        disabled={linking}
                      >Link</button>
                    </div>
                    {doc.document_type && (
                      <span style={{...S.badge('#6b7280'),marginTop:4,fontSize:10}}>{doc.document_type}</span>
                    )}
                  </div>
                ))}
              </div>
            )}
            {linkSearch.length >= 2 && linkResults.length === 0 && (
              <div style={{color:'#4b5563',fontSize:12,marginBottom:10}}>No matching documents found.</div>
            )}

            {/* Remarks */}
            <div>
              <label style={{...S.label,display:'block',marginBottom:4}}>Remarks (optional)</label>
              <input
                style={S.input}
                placeholder="Brief note about this link…"
                value={linkRemarks}
                onChange={e => setLinkRemarks(e.target.value)}
              />
            </div>
          </div>
        )}

        {/* Accordion per category */}
        {loading ? (
          <p style={{color:'#94a3b8',fontSize:13}}>Loading documents…</p>
        ) : (
          CATEGORIES.map(cat => {
            const docs = grouped[cat.key] ?? [];
            const open = openCats.has(cat.key);
            return (
              <div key={cat.key} style={S.accordion}>
                <div style={S.accHead(open)} onClick={() => toggleCat(cat.key)}>
                  <div style={{display:'flex',gap:8,alignItems:'center'}}>
                    <span>{cat.icon}</span>
                    <span style={{color: open?'#d1d5db':'#94a3b8',fontSize:12,fontWeight:600}}>{cat.label}</span>
                    <span style={S.badge(CAT_COLORS[cat.key] ?? '#6b7280')}>{docs.length}</span>
                  </div>
                  <span style={{color:'#4b5563',fontSize:12}}>{open ? '▲' : '▼'}</span>
                </div>
                {open && (
                  <div style={S.accBody}>
                    {docs.length === 0 ? (
                      <p style={{color:'#374151',fontSize:12,textAlign:'center',padding:'8px 0'}}>No documents in this category.</p>
                    ) : (
                      docs.map(doc => (
                        <div key={doc.id} style={S.docItem}>
                          <div style={{flex:1,minWidth:0}}>
                            <div style={{color:'#60a5fa',fontSize:11,fontFamily:'monospace',overflow:'hidden',textOverflow:'ellipsis',whiteSpace:'nowrap'}}>
                              {doc.document_number}
                            </div>
                            <div style={{color:'#d1d5db',fontSize:12,overflow:'hidden',textOverflow:'ellipsis',whiteSpace:'nowrap'}}>
                              {doc.document_title}
                            </div>
                            {doc.remarks && (
                              <div style={{color:'#6b7280',fontSize:10,marginTop:2}}>{doc.remarks}</div>
                            )}
                          </div>
                          <button
                            style={S.btn(undefined,true)}
                            title="Open in Preview"
                            onClick={() => doc.document_id && navigate(`/documents/${doc.document_id}/preview`)}
                            disabled={!doc.document_id}
                          >👁</button>
                          <button
                            style={S.btn(undefined,true)}
                            title="Unlink"
                            onClick={() => handleUnlink(doc)}
                          >✕</button>
                        </div>
                      ))
                    )}
                  </div>
                )}
              </div>
            );
          })
        )}

        {total >= 100 && (
          <div style={{color:'#f59e0b',fontSize:11,textAlign:'center',marginTop:10}}>
            ⚠ Maximum 100 documents reached.
          </div>
        )}
      </div>
    </div>
  );
}

// ── Tech Eval Docs Panel (carried forward, unchanged logic) ───────────────────
function TechEvalDocsPanel({ plNumber }: { plNumber: string }) {
  const MAX_DOCS = 3;
  const [docs,     setDocs]     = useState<TechEvalDoc[]>([]);
  const [loading,  setLoading]  = useState(true);
  const [msg,      setMsg]      = useState<{t:'ok'|'err';s:string}|null>(null);
  const [uploading,setUploading]= useState(false);
  const [showForm, setShowForm] = useState(false);
  const [slot, setSlot] = useState({ tender_number:'', eval_year:String(new Date().getFullYear()), file:null as File|null });
  const fileRef = useRef<HTMLInputElement>(null);

  const showMsg = (t:'ok'|'err', s:string) => { setMsg({t,s}); setTimeout(()=>setMsg(null),4000); };

  const loadDocs = () => {
    setLoading(true);
    plMasterService.listTechEvalDocs(plNumber)
      .then(d => setDocs(d.results ?? d))
      .catch(() => showMsg('err','Could not load evaluation documents.'))
      .finally(() => setLoading(false));
  };
  useEffect(() => { loadDocs(); }, [plNumber]);

  const handleUpload = async () => {
    if (!slot.tender_number.trim()) { showMsg('err','Tender number required.'); return; }
    if (!slot.file) { showMsg('err','Select a file.'); return; }
    if (docs.length >= MAX_DOCS) { showMsg('err',`Max ${MAX_DOCS} docs. Delete one first.`); return; }
    const ext = slot.file.name.split('.').pop()?.toLowerCase() ?? '';
    if (!['pdf','docx'].includes(ext)) { showMsg('err','Only PDF or DOCX accepted.'); return; }
    if (slot.file.size > 20*1024*1024) { showMsg('err','Max 20 MB.'); return; }
    setUploading(true);
    try {
      await plMasterService.uploadTechEvalDoc(plNumber, slot as any);
      showMsg('ok',`Uploaded — ${slot.file.name}`);
      setSlot({tender_number:'',eval_year:String(new Date().getFullYear()),file:null});
      if (fileRef.current) fileRef.current.value='';
      setShowForm(false); loadDocs();
    } catch (e:any) { showMsg('err', e?.detail ?? 'Upload failed.'); }
    finally { setUploading(false); }
  };

  const handleDelete = async (doc: TechEvalDoc) => {
    if (!window.confirm(`Delete "${doc.file_name}"?`)) return;
    try { await plMasterService.deleteTechEvalDoc(plNumber, doc.id); showMsg('ok','Removed.'); loadDocs(); }
    catch { showMsg('err','Delete failed.'); }
  };

  const fmtKB = (kb:number) => kb>=1024?`${(kb/1024).toFixed(1)} MB`:`${kb} KB`;

  return (
    <div style={S.card}>
      <div style={S.cardHead}>
        <div>
          <span style={S.cardTitle}>📄 Tech Eval Documents (Tender Ref)</span>
          <span style={{color:'#4b5563',fontSize:11,marginLeft:8}}>{docs.length}/{MAX_DOCS} uploaded</span>
        </div>
        {docs.length < MAX_DOCS && (
          <button style={S.btn('linear-gradient(135deg,#4b6cb7,#182848)',true)} onClick={()=>setShowForm(s=>!s)}>
            {showForm?'✕ Cancel':'⬆ Attach'}
          </button>
        )}
      </div>
      <div style={S.cardBody}>
        {msg && <div style={S.alert(msg.t)}>{msg.s}</div>}

        {showForm && (
          <div style={{background:'#1a2238',border:'1px solid #2d3555',borderRadius:8,padding:14,marginBottom:14}}>
            <div style={{display:'grid',gridTemplateColumns:'1fr 1fr',gap:'10px 16px',marginBottom:12}}>
              <div>
                <label style={{...S.label,display:'block',marginBottom:4}}>Tender Number *</label>
                <input style={S.input} placeholder="TEN/EL/2024-25/001"
                  value={slot.tender_number} onChange={e=>setSlot(s=>({...s,tender_number:e.target.value}))}/>
              </div>
              <div>
                <label style={{...S.label,display:'block',marginBottom:4}}>Eval Year *</label>
                <input type="number" style={S.input} min={2000} max={2099}
                  value={slot.eval_year} onChange={e=>setSlot(s=>({...s,eval_year:e.target.value}))}/>
              </div>
              <div style={{gridColumn:'1/-1'}}>
                <label style={{...S.label,display:'block',marginBottom:4}}>File * (PDF or DOCX, max 20 MB)</label>
                <input ref={fileRef} type="file"
                  accept=".pdf,.docx,application/pdf,application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                  style={{...S.input,padding:'5px 8px',cursor:'pointer'}}
                  onChange={e=>setSlot(s=>({...s,file:e.target.files?.[0]??null}))}/>
              </div>
            </div>
            <div style={{display:'flex',gap:8}}>
              <button style={S.btn('linear-gradient(135deg,#4b6cb7,#182848)')} onClick={handleUpload} disabled={uploading}>
                {uploading?'⏳ Uploading…':'💾 Upload & Attach'}
              </button>
              <button style={S.btn()} onClick={()=>setShowForm(false)}>Cancel</button>
            </div>
          </div>
        )}

        {loading ? <p style={{color:'#94a3b8',fontSize:13}}>Loading…</p>
          : docs.length === 0 ? (
            <div style={{textAlign:'center',padding:'18px 0',color:'#4b5563',fontSize:13}}>
              📂 No evaluation documents attached yet.
            </div>
          ) : docs.map((doc,i) => (
            <div key={doc.id} style={{...S.docItem,marginBottom:8}}>
              <span style={{color:'#60a5fa',fontSize:11,fontWeight:700,minWidth:14}}>{i+1}</span>
              <span style={S.badge(doc.file_format==='PDF'?'#ef4444':'#3b82f6')}>{doc.file_format}</span>
              <div style={{flex:1,minWidth:0}}>
                <div style={{color:'#d1d5db',fontSize:12,fontWeight:600,overflow:'hidden',textOverflow:'ellipsis',whiteSpace:'nowrap'}}>{doc.file_name}</div>
                <div style={{color:'#6b7280',fontSize:10,marginTop:2}}>Tender: {doc.tender_number} · {doc.eval_year} · {fmtKB(doc.file_size_kb)}</div>
              </div>
              <a href={doc.download_url} download={doc.file_name} target="_blank" rel="noreferrer"
                style={{...S.btn(undefined,true),textDecoration:'none'}}>⬇</a>
              <button style={S.btn(undefined,true)} onClick={()=>handleDelete(doc)}>🗑</button>
            </div>
          ))
        }
      </div>
    </div>
  );
}

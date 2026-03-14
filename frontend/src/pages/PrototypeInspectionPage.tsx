// =============================================================================
// FILE: frontend/src/pages/PrototypeInspectionPage.tsx
// BUG FIX 1: handleClosePunch was calling closePunchItem(inspectionId, punchId)
//            — inspectionId arg is WRONG, correct call is closePunchItem(punchId)
// BUG FIX 2: createPunchItem was being called — now matches renamed service method
// =============================================================================
import React, { useState, useEffect, useCallback } from 'react';
import { PageHeader, Btn, SearchBar, ConfirmDialog, Toast } from '../components/common';
import type { ToastMsg } from '../components/common';
import { prototypeService } from '../services/prototypeService';
import './PrototypeInspectionPage.css';

type PIView = 'list' | 'detail' | 'form';

export default function PrototypeInspectionPage() {
  const [view,     setView]     = useState<PIView>('list');
  const [activeId, setActiveId] = useState<number|null>(null);
  const [editItem, setEditItem] = useState<any|null>(null);

  return (
    <div className="pi-page">
      {view === 'list'   && <PIList  onView={id => { setActiveId(id); setView('detail'); }}
                                     onNew={() => { setEditItem(null); setView('form'); }} />}
      {view === 'detail' && activeId && <PIDetail inspectionId={activeId} onBack={() => setView('list')} />}
      {view === 'form'   && <PIForm  item={editItem} onDone={() => setView('list')} />}
    </div>
  );
}

// ─── Inspection List ──────────────────────────────────────────────────────────────────────
function PIList({ onView, onNew }: { onView:(id:number)=>void; onNew:()=>void }) {
  const [items,   setItems]   = useState<any[]>([]);
  const [total,   setTotal]   = useState(0);
  const [page,    setPage]    = useState(1);
  const [search,  setSearch]  = useState('');
  const [status,  setStatus]  = useState('');
  const [loading, setLoading] = useState(false);
  const [toast,   setToast]   = useState<ToastMsg|null>(null);
  const PAGE_SIZE = 20;

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const p: Record<string,string> = { page: String(page), page_size: String(PAGE_SIZE) };
      if (search) p.search = search;
      if (status) p.status = status;
      const data = await prototypeService.listInspections(p);
      setItems(data.results ?? (data as any) ?? []);
      setTotal(data.count ?? (data as any).total_count ?? 0);
    } catch { setToast({ type:'error', text:'Failed to load inspections.' }); }
    finally { setLoading(false); }
  }, [page, search, status]);

  useEffect(() => { load(); }, [load]);

  const STATUS_CLS: Record<string,string> = {
    OPEN:'pi-badge-open', IN_PROGRESS:'pi-badge-inprogress',
    PASS:'pi-badge-pass', FAIL:'pi-badge-fail', CLOSED:'pi-badge-closed',
  };
  const totalPages = Math.ceil(total / PAGE_SIZE);

  return (
    <div>
      <PageHeader title="Prototype Inspection" subtitle="Prototype loco inspection records and punch lists">
        <Btn size="sm" onClick={onNew}>+ New Inspection</Btn>
      </PageHeader>
      <Toast msg={toast} onClose={() => setToast(null)} />

      <div className="pi-toolbar">
        <SearchBar value={search} onChange={v => { setSearch(v); setPage(1); }}
          placeholder="Search loco no, inspection type…" width={300} />
        <select className="pi-select" value={status} onChange={e => { setStatus(e.target.value); setPage(1); }}>
          <option value="">All Status</option>
          <option value="OPEN">Open</option>
          <option value="IN_PROGRESS">In Progress</option>
          <option value="PASS">Pass</option>
          <option value="FAIL">Fail</option>
          <option value="CLOSED">Closed</option>
        </select>
        <Btn size="sm" variant="ghost" onClick={load}>↺ Refresh</Btn>
      </div>

      <div className="pi-table-wrap">
        <table className="pi-table">
          <thead><tr>
            <th>Loco No.</th><th>Loco Class</th><th>Inspection Type</th>
            <th>Inspection Date</th><th>Inspector</th><th>Status</th>
            <th>Punch Items</th><th>Actions</th>
          </tr></thead>
          <tbody>
            {loading && <tr><td colSpan={8} className="pi-center pi-muted">Loading…</td></tr>}
            {!loading && items.length===0 && <tr><td colSpan={8} className="pi-center pi-muted">No inspection records found.</td></tr>}
            {items.map(ins => (
              <tr key={ins.id}>
                <td className="pi-mono">{ins.loco_number ?? '—'}</td>
                <td><span className="pi-badge pi-badge-blue">{ins.loco_class ?? '—'}</span></td>
                <td>{ins.inspection_type ?? '—'}</td>
                <td className="pi-muted">{ins.inspection_date ?? '—'}</td>
                <td className="pi-muted">{ins.inspector_name ?? ins.inspector ?? '—'}</td>
                <td><span className={`pi-badge ${STATUS_CLS[ins.status] ?? ''}`}>{ins.status}</span></td>
                <td className="pi-center">
                  <span className={`pi-punch-count${(ins.open_punch_items ?? 0) > 0 ? ' pi-punch-count--open' : ''}`}>
                    {ins.open_punch_items ?? 0} open
                  </span>
                </td>
                <td className="pi-actions">
                  <Btn size="sm" variant="ghost" onClick={() => onView(ins.id)}>👁 View</Btn>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div className="pi-pagination">
        <span className="pi-muted">{total} inspections</span>
        <div className="pi-page-btns">
          <Btn size="sm" variant="secondary" disabled={page<=1} onClick={() => setPage(p=>p-1)}>← Prev</Btn>
          <span>Page {page} / {totalPages||1}</span>
          <Btn size="sm" variant="secondary" disabled={page>=totalPages} onClick={() => setPage(p=>p+1)}>Next →</Btn>
        </div>
      </div>
    </div>
  );
}

// ─── Inspection Detail (with Punch List) ──────────────────────────────────────────────────────────────────
function PIDetail({ inspectionId, onBack }: { inspectionId:number; onBack:()=>void }) {
  const [ins,         setIns]         = useState<any>(null);
  const [punches,     setPunches]     = useState<any[]>([]);
  const [loading,     setLoading]     = useState(true);
  const [toast,       setToast]       = useState<ToastMsg|null>(null);
  const [newPunch,    setNewPunch]    = useState('');
  const [addingPunch, setAddingPunch] = useState(false);

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const [i, p] = await Promise.all([
        prototypeService.getInspection(inspectionId),
        prototypeService.listPunchItems(inspectionId).catch(() => ({ results: [], count: 0 })),
      ]);
      setIns(i);
      setPunches(Array.isArray(p) ? p : (p as any).results ?? []);
    } catch { setToast({ type:'error', text:'Failed to load inspection.' }); }
    finally { setLoading(false); }
  }, [inspectionId]);

  useEffect(() => { load(); }, [load]);

  const handleAddPunch = async () => {
    if (!newPunch.trim()) return;
    setAddingPunch(true);
    try {
      // BUG FIX: was createPunchItem (name now matches service)
      await prototypeService.createPunchItem(inspectionId, { description: newPunch, status: 'OPEN' });
      setNewPunch('');
      load();
      setToast({ type:'success', text:'Punch item added.' });
    } catch { setToast({ type:'error', text:'Failed to add punch item.' }); }
    finally { setAddingPunch(false); }
  };

  const handleClosePunch = async (punchId: number) => {
    try {
      // BUG FIX: was closePunchItem(inspectionId, punchId) — inspectionId arg removed.
      // Correct: closePunchItem(punchId, remarks?)
      await prototypeService.closePunchItem(punchId);
      load();
      setToast({ type:'success', text:'Punch item closed.' });
    } catch { setToast({ type:'error', text:'Failed to close punch item.' }); }
  };

  const handleCloseInspection = async () => {
    try {
      await prototypeService.closeInspection(inspectionId);
      load();
      setToast({ type:'success', text:'Inspection closed.' });
    } catch { setToast({ type:'error', text:'Failed to close inspection.' }); }
  };

  if (loading) return <div className="pi-loading">⏳ Loading…</div>;

  return (
    <div>
      <PageHeader
        title={`Inspection #${inspectionId}`}
        subtitle={`${ins?.loco_class ?? ''} — ${ins?.loco_number ?? ''} — ${ins?.inspection_type ?? ''}`}
        back={onBack}
      >
        {ins?.status !== 'CLOSED' && (
          <Btn size="sm" variant="primary" onClick={handleCloseInspection}>✓ Close Inspection</Btn>
        )}
      </PageHeader>
      <Toast msg={toast} onClose={() => setToast(null)} />

      <div className="pi-detail-grid">
        <div className="pi-card">
          <div className="pi-card-title">📋 Inspection Details</div>
          <div className="pi-card-body">
            <table className="pi-meta-table">
              <tbody>
                {([
                  ['Loco Number',     ins?.loco_number ?? '—'],
                  ['Loco Class',      ins?.loco_class ?? '—'],
                  ['Inspection Type', ins?.inspection_type ?? '—'],
                  ['Date',            ins?.inspection_date ?? '—'],
                  ['Inspector',       ins?.inspector_name ?? ins?.inspector ?? '—'],
                  ['Status',          ins?.status ?? '—'],
                  ['Result',          ins?.result ?? '—'],
                  ['Remarks',         ins?.remarks ?? '—'],
                ] as [string, string][]).map(([k, v], i) => (
                  <tr key={i}>
                    <td className="pi-meta-key">{k}</td>
                    <td className="pi-meta-val">{v}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        <div className="pi-card">
          <div className="pi-card-title">📌 Punch List ({punches.filter((p: any) => p.status === 'OPEN').length} open)</div>
          <div className="pi-card-body">
            {punches.length === 0 && (
              <div className="pi-no-punch">No punch items. Inspection is clean ✅</div>
            )}
            {punches.map((p: any, i: number) => (
              <div key={p.id ?? i} className={`pi-punch-item${p.status === 'CLOSED' ? ' pi-punch-item--closed' : ''}`}>
                <span className={`pi-punch-status pi-punch-status--${p.status?.toLowerCase()}`}>●</span>
                <span className="pi-punch-desc">{p.description}</span>
                {p.status === 'OPEN' && (
                  // BUG FIX: was closePunchItem(inspectionId, p.id) — fixed to closePunchItem(p.id)
                  <Btn size="sm" variant="ghost" onClick={() => handleClosePunch(p.id)}>✓ Close</Btn>
                )}
              </div>
            ))}

            {ins?.status !== 'CLOSED' && (
              <div className="pi-add-punch">
                <input
                  className="pi-punch-input"
                  value={newPunch}
                  onChange={e => setNewPunch(e.target.value)}
                  onKeyDown={e => e.key === 'Enter' && handleAddPunch()}
                  placeholder="Add punch item (press Enter or click +)…"
                />
                <Btn size="sm" onClick={handleAddPunch} loading={addingPunch}>+ Add</Btn>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

// ─── New / Edit Inspection Form ───────────────────────────────────────────────────────────────────────
function PIForm({ item, onDone }: { item: any|null; onDone: ()=>void }) {
  const [form, setForm] = useState({
    loco_number:     item?.loco_number     ?? '',
    loco_class:      item?.loco_class      ?? 'WAG-9',
    inspection_type: item?.inspection_type ?? 'PROTOTYPE',
    inspection_date: item?.inspection_date ?? new Date().toISOString().slice(0, 10),
    inspector:       item?.inspector       ?? '',
    remarks:         item?.remarks         ?? '',
  });
  const [saving, setSaving] = useState(false);
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [toast,  setToast]  = useState<ToastMsg|null>(null);

  const LOCO  = ['WAG-9','WAG-9H','WAP-7','WAP-5','WAG-12B','MEMU','DEMU'];
  const TYPES = ['PROTOTYPE','PERIODIC','SPECIAL','RETURN_TO_SERVICE','PDI'];

  const sf = (k: string, v: string) => {
    setForm(f => ({ ...f, [k]: v }));
    setErrors(e => ({ ...e, [k]: '' }));
  };

  const validate = () => {
    const e: Record<string, string> = {};
    if (!form.loco_number) e.loco_number = 'Required';
    if (!form.inspector)   e.inspector   = 'Required';
    setErrors(e);
    return Object.keys(e).length === 0;
  };

  const handleSave = async () => {
    if (!validate()) return;
    setSaving(true);
    try {
      if (item) await prototypeService.updateInspection(item.id, form);
      else      await prototypeService.createInspection(form);
      onDone();
    } catch (err: any) {
      setErrors({ _global: JSON.stringify(err?.response?.data ?? 'Save failed.') });
    } finally { setSaving(false); }
  };

  return (
    <div>
      <PageHeader title={item ? 'Edit Inspection' : 'New Inspection'} back={onDone} />
      <Toast msg={toast} onClose={() => setToast(null)} />
      <div className="pi-form">
        {errors._global && <div className="pi-alert-err">{errors._global}</div>}
        <div className="pi-form-grid">
          <div className="pi-field">
            <label>Loco Number <span className="pi-req">*</span></label>
            <input value={form.loco_number} onChange={e => sf('loco_number', e.target.value)} placeholder="e.g. 31001" />
            {errors.loco_number && <span className="pi-err">{errors.loco_number}</span>}
          </div>
          <div className="pi-field">
            <label>Loco Class</label>
            <select value={form.loco_class} onChange={e => sf('loco_class', e.target.value)}>
              {LOCO.map(l => <option key={l} value={l}>{l}</option>)}
            </select>
          </div>
          <div className="pi-field">
            <label>Inspection Type</label>
            <select value={form.inspection_type} onChange={e => sf('inspection_type', e.target.value)}>
              {TYPES.map(t => <option key={t} value={t}>{t.replace(/_/g, ' ')}</option>)}
            </select>
          </div>
          <div className="pi-field">
            <label>Inspection Date</label>
            <input type="date" value={form.inspection_date} onChange={e => sf('inspection_date', e.target.value)} />
          </div>
          <div className="pi-field">
            <label>Inspector Name <span className="pi-req">*</span></label>
            <input value={form.inspector} onChange={e => sf('inspector', e.target.value)} placeholder="Inspector name…" />
            {errors.inspector && <span className="pi-err">{errors.inspector}</span>}
          </div>
          <div className="pi-field pi-full">
            <label>Remarks</label>
            <textarea rows={3} value={form.remarks} onChange={e => sf('remarks', e.target.value)} />
          </div>
        </div>
        <div className="pi-form-actions">
          <Btn variant="secondary" onClick={onDone} disabled={saving}>Cancel</Btn>
          <Btn variant="primary"   onClick={handleSave} loading={saving}>💾 Save Inspection</Btn>
        </div>
      </div>
    </div>
  );
}

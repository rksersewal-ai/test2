// =============================================================================
// FILE: frontend/src/pages/WorkLedger/WorkLedgerPage.tsx
// Full Work Ledger: list, create, edit, submit, verify, reports
// =============================================================================
import React, { useState, useEffect, useCallback, useRef } from 'react';
import { PageHeader, Btn, SearchBar, ConfirmDialog, Toast } from '../../components/common';
import type { ToastMsg } from '../../components/common';
import { workLedgerService } from '../../services/workLedgerService';
import './WorkLedgerPage.css';

type WLView = 'list' | 'form';
type FormMode = 'create' | 'edit';

const STATUS_CLASS: Record<string,string> = {
  DRAFT:'wl-badge-draft', SUBMITTED:'wl-badge-submitted',
  VERIFIED:'wl-badge-verified', APPROVED:'wl-badge-approved', RETURNED:'wl-badge-returned',
};

export default function WorkLedgerPage() {
  const [view,    setView]    = useState<WLView>('list');
  const [editId,  setEditId]  = useState<number|null>(null);

  const handleEdit = (id: number) => { setEditId(id); setView('form'); };
  const handleNew  = ()           => { setEditId(null); setView('form'); };
  const handleBack = ()           => { setEditId(null); setView('list'); };

  return (
    <div className="wl-page">
      {view === 'list'
        ? <WLList onEdit={handleEdit} onNew={handleNew} />
        : <WLForm mode={editId ? 'edit' : 'create'} entryId={editId} onDone={handleBack} />}
    </div>
  );
}

// ─────────────────────────────────────────────────────────────────────────────
// List View
// ─────────────────────────────────────────────────────────────────────────────
function WLList({ onEdit, onNew }: { onEdit:(id:number)=>void; onNew:()=>void }) {
  const [entries,  setEntries]  = useState<any[]>([]);
  const [total,    setTotal]    = useState(0);
  const [page,     setPage]     = useState(1);
  const [search,   setSearch]   = useState('');
  const [status,   setStatus]   = useState('');
  const [loading,  setLoading]  = useState(false);
  const [toast,    setToast]    = useState<ToastMsg|null>(null);
  const [confirm,  setConfirm]  = useState<number|null>(null);
  const [verifyTarget, setVerifyTarget] = useState<any|null>(null);
  const [remarks,  setRemarks]  = useState('');
  const PAGE_SIZE = 20;

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const p: Record<string,string> = { page: String(page), page_size: String(PAGE_SIZE) };
      if (search) p.search = search;
      if (status) p.status = status;
      const data = await workLedgerService.listEntries(p);
      setEntries(data.results ?? []);
      setTotal(data.count ?? 0);
    } catch { setToast({ type:'error', text:'Failed to load work entries.' }); }
    finally { setLoading(false); }
  }, [page, search, status]);

  useEffect(() => { load(); }, [load]);

  const handleDelete = async () => {
    if (!confirm) return;
    try { await workLedgerService.deleteEntry(confirm); setToast({ type:'success', text:'Entry deleted.' }); load(); }
    catch { setToast({ type:'error', text:'Delete failed.' }); }
    finally { setConfirm(null); }
  };

  const handleSubmit = async (id: number) => {
    try { await workLedgerService.submitEntry(id); setToast({ type:'success', text:'Entry submitted for verification.' }); load(); }
    catch { setToast({ type:'error', text:'Submit failed.' }); }
  };

  const handleVerify = async (action: 'VERIFY'|'RETURN') => {
    if (!verifyTarget) return;
    try {
      await workLedgerService.verifyEntry(verifyTarget.id, action, remarks);
      setToast({ type:'success', text: action === 'VERIFY' ? 'Entry verified.' : 'Entry returned for correction.' });
      load();
    } catch { setToast({ type:'error', text:'Action failed.' }); }
    finally { setVerifyTarget(null); setRemarks(''); }
  };

  const handleDownload = async (format: 'pdf'|'excel') => {
    const now = new Date();
    try {
      const blob = await workLedgerService.downloadReport(now.getFullYear(), now.getMonth()+1, format);
      const url  = URL.createObjectURL(blob);
      const a    = document.createElement('a');
      a.href = url;
      a.download = `WorkReport_${now.getFullYear()}_${String(now.getMonth()+1).padStart(2,'0')}.${format==='pdf'?'pdf':'xlsx'}`;
      a.click();
      URL.revokeObjectURL(url);
    } catch { setToast({ type:'error', text:'Report download failed.' }); }
  };

  const totalPages = Math.ceil(total / PAGE_SIZE);

  return (
    <div>
      <PageHeader title="Work Ledger" subtitle="Daily work entries — submit, verify, download reports">
        <Btn size="sm" variant="secondary" onClick={() => handleDownload('excel')}>⬇ Excel Report</Btn>
        <Btn size="sm" variant="secondary" onClick={() => handleDownload('pdf')}>⬇ PDF Report</Btn>
        <Btn size="sm" onClick={onNew}>+ New Entry</Btn>
      </PageHeader>

      <Toast msg={toast} onClose={() => setToast(null)} />

      {/* Delete confirm */}
      <ConfirmDialog
        open={!!confirm}
        title="Delete Entry" message="Delete this work entry? This cannot be undone."
        confirmLabel="Delete"
        onConfirm={handleDelete} onCancel={() => setConfirm(null)}
      />

      {/* Verify / Return modal */}
      {verifyTarget && (
        <div className="wl-modal-overlay" onClick={() => setVerifyTarget(null)}>
          <div className="wl-modal" onClick={e => e.stopPropagation()}>
            <div className="wl-modal-title">Verify Entry</div>
            <p style={{fontSize:13,color:'#444',marginBottom:12}}>Entry: <strong>{verifyTarget.work_description?.slice(0,60)}</strong></p>
            <label style={{fontSize:12,fontWeight:600}}>Remarks (optional)</label>
            <textarea className="wl-remarks" rows={3} value={remarks} onChange={e => setRemarks(e.target.value)} />
            <div className="wl-modal-actions">
              <Btn variant="secondary" size="sm" onClick={() => setVerifyTarget(null)}>Cancel</Btn>
              <Btn variant="danger"    size="sm" onClick={() => handleVerify('RETURN')}>↩ Return</Btn>
              <Btn variant="primary"   size="sm" onClick={() => handleVerify('VERIFY')}>✓ Verify</Btn>
            </div>
          </div>
        </div>
      )}

      {/* Filters */}
      <div className="wl-toolbar">
        <SearchBar value={search} onChange={v => { setSearch(v); setPage(1); }} placeholder="Search description, ref no., eOffice…" width={320} />
        <select value={status} onChange={e => { setStatus(e.target.value); setPage(1); }}>
          <option value="">All Status</option>
          <option value="DRAFT">Draft</option>
          <option value="SUBMITTED">Submitted</option>
          <option value="VERIFIED">Verified</option>
          <option value="APPROVED">Approved</option>
          <option value="RETURNED">Returned</option>
        </select>
        <Btn size="sm" variant="ghost" onClick={load}>↺ Refresh</Btn>
      </div>

      {/* Table */}
      <div className="wl-table-wrap">
        <table className="wl-table">
          <thead><tr>
            <th>Date</th><th>Description</th><th>Category</th>
            <th>Work Type</th><th>Hrs</th><th>Ref No.</th>
            <th>Status</th><th>Actions</th>
          </tr></thead>
          <tbody>
            {loading && <tr><td colSpan={8} className="wl-center wl-muted">Loading…</td></tr>}
            {!loading && entries.length === 0 && <tr><td colSpan={8} className="wl-center wl-muted">No work entries found.</td></tr>}
            {entries.map(e => (
              <tr key={e.id}>
                <td className="wl-muted">{e.work_date}</td>
                <td className="wl-desc">{e.work_description ?? '—'}</td>
                <td className="wl-muted">{e.category_name ?? '—'}</td>
                <td>{e.work_type ?? '—'}</td>
                <td className="wl-center">{e.hours_spent ?? '—'}</td>
                <td className="wl-mono">{e.reference_number ?? e.eoffice_file_no ?? '—'}</td>
                <td><span className={`wl-badge ${STATUS_CLASS[e.status] ?? ''}`}>{e.status}</span></td>
                <td className="wl-actions">
                  {e.status === 'DRAFT' && (
                    <>
                      <Btn size="sm" variant="secondary" onClick={() => onEdit(e.id)}>✏️</Btn>
                      <Btn size="sm" variant="gold"      onClick={() => handleSubmit(e.id)}>↑ Submit</Btn>
                      <Btn size="sm" variant="danger"    onClick={() => setConfirm(e.id)}>🗑</Btn>
                    </>
                  )}
                  {e.status === 'SUBMITTED' && (
                    <Btn size="sm" variant="primary" onClick={() => setVerifyTarget(e)}>✓ Verify</Btn>
                  )}
                  {(e.status === 'RETURNED') && (
                    <Btn size="sm" variant="secondary" onClick={() => onEdit(e.id)}>✏️ Correct</Btn>
                  )}
                  {e.status === 'VERIFIED' && <span className="wl-muted">✓ Done</span>}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div className="wl-pagination">
        <span className="wl-muted">Showing {entries.length} of {total}</span>
        <div className="wl-page-btns">
          <Btn size="sm" variant="secondary" disabled={page<=1} onClick={() => setPage(p=>p-1)}>← Prev</Btn>
          <span>Page {page} / {totalPages||1}</span>
          <Btn size="sm" variant="secondary" disabled={page>=totalPages} onClick={() => setPage(p=>p+1)}>Next →</Btn>
        </div>
      </div>
    </div>
  );
}

// ─────────────────────────────────────────────────────────────────────────────
// Create / Edit Form
// ─────────────────────────────────────────────────────────────────────────────
function WLForm({ mode, entryId, onDone }: { mode:FormMode; entryId:number|null; onDone:()=>void }) {
  const [form, setForm] = useState<any>({
    work_date: new Date().toISOString().slice(0,10),
    work_description:'', category:'', work_type:'DRAWING_REVIEW',
    hours_spent:'', reference_number:'', eoffice_file_no:'', remarks:'',
  });
  const [categories, setCategories] = useState<any[]>([]);
  const [saving,  setSaving]  = useState(false);
  const [loading, setLoading] = useState(false);
  const [errors,  setErrors]  = useState<Record<string,string>>({});
  const [toast,   setToast]   = useState<ToastMsg|null>(null);

  const WORK_TYPES = [
    'DRAWING_REVIEW','SPEC_REVIEW','BOM_UPDATE','CORRESPONDENCE',
    'INSPECTION','TESTING','REPORT','MEETING','OTHER',
  ];

  useEffect(() => {
    workLedgerService.listCategories().then(data => setCategories(Array.isArray(data) ? data : data.results ?? []));
    if (mode === 'edit' && entryId) {
      setLoading(true);
      workLedgerService.getEntry(entryId).then(data => {
        setForm({
          work_date:        data.work_date,
          work_description: data.work_description,
          category:         data.category,
          work_type:        data.work_type,
          hours_spent:      data.hours_spent,
          reference_number: data.reference_number ?? '',
          eoffice_file_no:  data.eoffice_file_no ?? '',
          remarks:          data.remarks ?? '',
        });
      }).finally(() => setLoading(false));
    }
  }, [mode, entryId]);

  const validate = () => {
    const e: Record<string,string> = {};
    if (!form.work_date)        e.work_date        = 'Required';
    if (!form.work_description) e.work_description = 'Required';
    if (!form.work_type)        e.work_type        = 'Required';
    setErrors(e);
    return Object.keys(e).length === 0;
  };

  const handleSave = async () => {
    if (!validate()) return;
    setSaving(true);
    try {
      if (mode === 'create') await workLedgerService.createEntry(form);
      else if (entryId) await workLedgerService.updateEntry(entryId, form);
      setToast({ type:'success', text:'Entry saved.' });
      setTimeout(onDone, 600);
    } catch (err: any) {
      setErrors({ _global: JSON.stringify(err?.response?.data ?? 'Save failed.') });
    } finally { setSaving(false); }
  };

  const sf = (field: string, val: string) => { setForm((f:any) => ({...f,[field]:val})); setErrors(e => ({...e,[field]:'' })); };

  if (loading) return <div className="wl-loading">Loading…</div>;

  return (
    <div>
      <PageHeader
        title={mode === 'create' ? 'New Work Entry' : 'Edit Work Entry'}
        back={onDone}
      />
      <Toast msg={toast} onClose={() => setToast(null)} />

      <div className="wl-form">
        {errors._global && <div className="wl-alert-error">{errors._global}</div>}

        <div className="wl-form-grid">
          <div className="wl-field">
            <label>Work Date <span className="wl-req">*</span></label>
            <input type="date" value={form.work_date} onChange={e => sf('work_date', e.target.value)} />
            {errors.work_date && <span className="wl-err">{errors.work_date}</span>}
          </div>

          <div className="wl-field">
            <label>Work Type <span className="wl-req">*</span></label>
            <select value={form.work_type} onChange={e => sf('work_type', e.target.value)}>
              {WORK_TYPES.map(t => <option key={t} value={t}>{t.replace(/_/g,' ')}</option>)}
            </select>
            {errors.work_type && <span className="wl-err">{errors.work_type}</span>}
          </div>

          <div className="wl-field">
            <label>Category</label>
            <select value={form.category} onChange={e => sf('category', e.target.value)}>
              <option value="">— Select Category —</option>
              {categories.map((c:any) => <option key={c.id} value={c.id}>{c.category_name}</option>)}
            </select>
          </div>

          <div className="wl-field">
            <label>Hours Spent</label>
            <input type="number" min="0" step="0.5" value={form.hours_spent}
              onChange={e => sf('hours_spent', e.target.value)} />
          </div>

          <div className="wl-field">
            <label>Reference Number</label>
            <input type="text" placeholder="Drawing/Spec/PLW ref no." value={form.reference_number}
              onChange={e => sf('reference_number', e.target.value)} />
          </div>

          <div className="wl-field">
            <label>eOffice File No.</label>
            <input type="text" placeholder="eOffice number if applicable" value={form.eoffice_file_no}
              onChange={e => sf('eoffice_file_no', e.target.value)} />
          </div>

          <div className="wl-field wl-full">
            <label>Work Description <span className="wl-req">*</span></label>
            <textarea rows={4} value={form.work_description}
              onChange={e => sf('work_description', e.target.value)}
              placeholder="Describe the work done in detail…" />
            {errors.work_description && <span className="wl-err">{errors.work_description}</span>}
          </div>

          <div className="wl-field wl-full">
            <label>Remarks</label>
            <textarea rows={2} value={form.remarks}
              onChange={e => sf('remarks', e.target.value)} />
          </div>
        </div>

        <div className="wl-form-actions">
          <Btn variant="secondary" onClick={onDone} disabled={saving}>Cancel</Btn>
          <Btn variant="primary"   onClick={handleSave} loading={saving}>
            {mode === 'create' ? '💾 Save Entry' : '💾 Save Changes'}
          </Btn>
        </div>
      </div>
    </div>
  );
}

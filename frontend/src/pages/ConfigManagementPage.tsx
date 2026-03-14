// =============================================================================
// FILE: frontend/src/pages/ConfigManagementPage.tsx
// Real-API Config Management: Loco Configs tab + ECN Register tab
// =============================================================================
import React, { useState, useEffect, useCallback } from 'react';
import { PageHeader, Btn, SearchBar, ConfirmDialog, Toast } from './common_import';
import type { ToastMsg } from './common_import';
import { configService } from '../services/configService';
import './ConfigManagementPage.css';

// Re-export helper so we avoid circular imports from common/index
import { Btn as BtnC, PageHeader as PHC, SearchBar as SBC,
         ConfirmDialog as CDC, Toast as TC } from '../components/common';
const _Btn = BtnC, _PH = PHC, _SB = SBC, _CD = CDC, _T = TC;

type CTab = 'configs' | 'ecn';

const STATUS_CLS: Record<string, string> = {
  APPROVED: 'cfg-badge-approved', PENDING: 'cfg-badge-pending',
  SUPERSEDED: 'cfg-badge-superseded', REJECTED: 'cfg-badge-rejected',
};

export default function ConfigManagementPage() {
  const [tab, setTab] = useState<CTab>('configs');
  return (
    <div className="cfg-page">
      <_PH title="Configuration Management" subtitle="Loco configurations, ECN register, BOM change history" />
      <div className="cfg-tabs">
        <button className={`cfg-tab${tab==='configs'?' cfg-tab--active':''}`} onClick={() => setTab('configs')}>⚙️ Loco Configs</button>
        <button className={`cfg-tab${tab==='ecn'?' cfg-tab--active':''}`} onClick={() => setTab('ecn')}>📋 ECN Register</button>
      </div>
      <div className="cfg-body">
        {tab === 'configs' ? <LocoConfigsTab /> : <ECNTab />}
      </div>
    </div>
  );
}

// ─── Loco Configs Tab ──────────────────────────────────────────────────────────────
function LocoConfigsTab() {
  const [items,   setItems]   = useState<any[]>([]);
  const [total,   setTotal]   = useState(0);
  const [page,    setPage]    = useState(1);
  const [search,  setSearch]  = useState('');
  const [loading, setLoading] = useState(false);
  const [toast,   setToast]   = useState<ToastMsg|null>(null);
  const [confirm, setConfirm] = useState<number|null>(null);
  const [showForm, setShowForm] = useState(false);
  const [editItem, setEditItem] = useState<any|null>(null);
  const [locoFilter, setLocoFilter] = useState('');
  const [statusFilter, setStatusFilter] = useState('');
  const PAGE_SIZE = 20;

  const LOCO_TYPES = ['WAG-9','WAG-9H','WAG-9HH','WAP-7','WAP-5','WAG-12B','MEMU','DEMU'];

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const p: Record<string,string> = { page: String(page), page_size: String(PAGE_SIZE) };
      if (search)      p.search     = search;
      if (locoFilter)  p.loco_class = locoFilter;
      if (statusFilter) p.status    = statusFilter;
      const data = await configService.listConfigs(p);
      setItems(data.results ?? data ?? []);
      setTotal(data.count ?? data.total_count ?? 0);
    } catch { setToast({ type:'error', text:'Failed to load configurations.' }); }
    finally { setLoading(false); }
  }, [page, search, locoFilter, statusFilter]);

  useEffect(() => { load(); }, [load]);

  const handleDelete = async () => {
    if (!confirm) return;
    try { await configService.deleteConfig(confirm); setToast({ type:'success', text:'Config deleted.' }); load(); }
    catch { setToast({ type:'error', text:'Delete failed.' }); }
    finally { setConfirm(null); }
  };

  const totalPages = Math.ceil(total / PAGE_SIZE);

  return (
    <div>
      <_T msg={toast} onClose={() => setToast(null)} />
      <_CD open={!!confirm} title="Delete Config"
        message="Delete this loco configuration record? This cannot be undone."
        confirmLabel="Delete" onConfirm={handleDelete} onCancel={() => setConfirm(null)} />

      {showForm && (
        <ConfigForm
          item={editItem}
          locoTypes={LOCO_TYPES}
          onClose={() => { setShowForm(false); setEditItem(null); }}
          onSuccess={(msg) => { setShowForm(false); setEditItem(null); setToast({ type:'success', text: msg }); load(); }}
        />
      )}

      {/* Toolbar */}
      <div className="cfg-toolbar">
        <_SB value={search} onChange={v => { setSearch(v); setPage(1); }} placeholder="Search serial no, ECN ref…" width={260} />
        <select className="cfg-select" value={locoFilter} onChange={e => { setLocoFilter(e.target.value); setPage(1); }}>
          <option value="">All Loco Types</option>
          {LOCO_TYPES.map(t => <option key={t} value={t}>{t}</option>)}
        </select>
        <select className="cfg-select" value={statusFilter} onChange={e => { setStatusFilter(e.target.value); setPage(1); }}>
          <option value="">All Status</option>
          <option value="APPROVED">Approved</option>
          <option value="PENDING">Pending</option>
          <option value="SUPERSEDED">Superseded</option>
        </select>
        <_Btn size="sm" variant="ghost" onClick={load}>↺ Refresh</_Btn>
        <_Btn size="sm" onClick={() => { setEditItem(null); setShowForm(true); }}>+ New Config</_Btn>
      </div>

      {/* Table */}
      <div className="cfg-table-wrap">
        <table className="cfg-table">
          <thead><tr>
            <th>Loco Class</th><th>Serial No.</th><th>Config Ver.</th>
            <th>ECN Ref</th><th>Effective Date</th><th>Changed By</th>
            <th>Status</th><th>Actions</th>
          </tr></thead>
          <tbody>
            {loading && <tr><td colSpan={8} className="cfg-center cfg-muted">Loading…</td></tr>}
            {!loading && items.length===0 && <tr><td colSpan={8} className="cfg-center cfg-muted">No configurations found.</td></tr>}
            {items.map(c => (
              <tr key={c.id}>
                <td><span className="cfg-badge cfg-badge-blue">{c.loco_class ?? c.locoClass}</span></td>
                <td className="cfg-mono">{c.serial_no ?? c.serialNo}</td>
                <td className="cfg-mono cfg-purple">{c.config_version ?? c.configVersion}</td>
                <td className="cfg-mono cfg-gold">{c.ecn_ref ?? c.changeRef ?? '—'}</td>
                <td className="cfg-muted">{c.effective_date ?? c.effectiveDate ?? '—'}</td>
                <td className="cfg-muted">{c.changed_by ?? c.changedBy ?? '—'}</td>
                <td><span className={`cfg-badge ${STATUS_CLS[c.status] ?? ''}`}>{c.status}</span></td>
                <td className="cfg-actions">
                  <_Btn size="sm" variant="ghost"
                    onClick={() => { setEditItem(c); setShowForm(true); }}>✏️ Edit</_Btn>
                  <_Btn size="sm" variant="danger"
                    onClick={() => setConfirm(c.id)}>🗑</_Btn>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div className="cfg-pagination">
        <span className="cfg-muted">{total} configs total</span>
        <div className="cfg-page-btns">
          <_Btn size="sm" variant="secondary" disabled={page<=1} onClick={() => setPage(p=>p-1)}>← Prev</_Btn>
          <span>Page {page} / {totalPages||1}</span>
          <_Btn size="sm" variant="secondary" disabled={page>=totalPages} onClick={() => setPage(p=>p+1)}>Next →</_Btn>
        </div>
      </div>
    </div>
  );
}

// ─── ECN Register Tab ─────────────────────────────────────────────────────────────
function ECNTab() {
  const [items,   setItems]   = useState<any[]>([]);
  const [total,   setTotal]   = useState(0);
  const [page,    setPage]    = useState(1);
  const [search,  setSearch]  = useState('');
  const [loading, setLoading] = useState(false);
  const [toast,   setToast]   = useState<ToastMsg|null>(null);
  const PAGE_SIZE = 20;

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const p: Record<string,string> = { page: String(page), page_size: String(PAGE_SIZE) };
      if (search) p.search = search;
      const data = await configService.listECN(p);
      setItems(data.results ?? data ?? []);
      setTotal(data.count ?? data.total_count ?? 0);
    } catch { setToast({ type:'error', text:'Failed to load ECN records.' }); }
    finally { setLoading(false); }
  }, [page, search]);

  useEffect(() => { load(); }, [load]);

  const handleApprove = async (id: number) => {
    try { await configService.approveECN(id); setToast({ type:'success', text:'ECN approved.' }); load(); }
    catch { setToast({ type:'error', text:'Approve failed.' }); }
  };

  const totalPages = Math.ceil(total / PAGE_SIZE);

  return (
    <div>
      <_T msg={toast} onClose={() => setToast(null)} />
      <div className="cfg-toolbar">
        <_SB value={search} onChange={v => { setSearch(v); setPage(1); }} placeholder="Search ECN number, subject…" width={300} />
        <_Btn size="sm" variant="ghost" onClick={load}>↺ Refresh</_Btn>
        <_Btn size="sm" onClick={() => {}}>+ New ECN</_Btn>
      </div>

      <div className="cfg-table-wrap">
        <table className="cfg-table">
          <thead><tr>
            <th>ECN Number</th><th>Subject</th><th>Loco Class</th>
            <th>Raised By</th><th>Date</th><th>Status</th><th>Actions</th>
          </tr></thead>
          <tbody>
            {loading && <tr><td colSpan={7} className="cfg-center cfg-muted">Loading…</td></tr>}
            {!loading && items.length===0 && <tr><td colSpan={7} className="cfg-center cfg-muted">No ECN records found.</td></tr>}
            {items.map(e => (
              <tr key={e.id}>
                <td className="cfg-mono cfg-gold">{e.ecn_number ?? '—'}</td>
                <td className="cfg-desc">{e.subject ?? '—'}</td>
                <td><span className="cfg-badge cfg-badge-blue">{e.loco_class ?? '—'}</span></td>
                <td className="cfg-muted">{e.raised_by_name ?? e.raised_by ?? '—'}</td>
                <td className="cfg-muted">{e.date ?? '—'}</td>
                <td><span className={`cfg-badge ${STATUS_CLS[e.status] ?? ''}`}>{e.status}</span></td>
                <td className="cfg-actions">
                  {e.status === 'PENDING' && (
                    <_Btn size="sm" variant="primary" onClick={() => handleApprove(e.id)}>✓ Approve</_Btn>
                  )}
                  <_Btn size="sm" variant="ghost">👁 View</_Btn>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div className="cfg-pagination">
        <span className="cfg-muted">{total} ECN records</span>
        <div className="cfg-page-btns">
          <_Btn size="sm" variant="secondary" disabled={page<=1} onClick={() => setPage(p=>p-1)}>← Prev</_Btn>
          <span>Page {page} / {totalPages||1}</span>
          <_Btn size="sm" variant="secondary" disabled={page>=totalPages} onClick={() => setPage(p=>p+1)}>Next →</_Btn>
        </div>
      </div>
    </div>
  );
}

// ─── Config Form (Create / Edit) ────────────────────────────────────────────────────
function ConfigForm({ item, locoTypes, onClose, onSuccess }:{
  item: any|null; locoTypes: string[];
  onClose: ()=>void; onSuccess: (msg:string)=>void;
}) {
  const isEdit = !!item;
  const [form, setForm] = useState({
    loco_class:      item?.loco_class ?? item?.locoClass ?? '',
    serial_no:       item?.serial_no ?? item?.serialNo ?? '',
    config_version:  item?.config_version ?? item?.configVersion ?? '',
    ecn_ref:         item?.ecn_ref ?? item?.changeRef ?? '',
    effective_date:  item?.effective_date ?? item?.effectiveDate ?? '',
    changed_by:      item?.changed_by ?? item?.changedBy ?? '',
    status:          item?.status ?? 'PENDING',
    remarks:         item?.remarks ?? '',
  });
  const [saving, setSaving] = useState(false);
  const [errors, setErrors] = useState<Record<string,string>>({});

  const sf = (k: string, v: string) => { setForm(f => ({...f,[k]:v})); setErrors(e => ({...e,[k]:''})); };

  const validate = () => {
    const e: Record<string,string> = {};
    if (!form.loco_class)     e.loco_class    = 'Required';
    if (!form.serial_no)      e.serial_no     = 'Required';
    if (!form.config_version) e.config_version= 'Required';
    setErrors(e); return Object.keys(e).length === 0;
  };

  const handleSave = async () => {
    if (!validate()) return;
    setSaving(true);
    try {
      if (isEdit) await configService.updateConfig(item.id, form);
      else        await configService.createConfig(form);
      onSuccess(isEdit ? 'Config updated.' : 'Config created.');
    } catch (err: any) {
      setErrors({ _global: JSON.stringify(err?.response?.data ?? 'Save failed.') });
    } finally { setSaving(false); }
  };

  return (
    <div className="cfg-modal-overlay" onClick={onClose}>
      <div className="cfg-modal" onClick={e => e.stopPropagation()}>
        <div className="cfg-modal-header">
          <span>{isEdit ? '✏️ Edit Config' : '+ New Loco Config'}</span>
          <button className="cfg-modal-close" onClick={onClose}>✕</button>
        </div>
        <div className="cfg-modal-body">
          {errors._global && <div className="cfg-alert-err">{errors._global}</div>}
          <div className="cfg-form-grid">
            <div className="cfg-field">
              <label>Loco Class <span className="cfg-req">*</span></label>
              <select value={form.loco_class} onChange={e => sf('loco_class', e.target.value)}>
                <option value="">— Select —</option>
                {locoTypes.map(t => <option key={t} value={t}>{t}</option>)}
              </select>
              {errors.loco_class && <span className="cfg-err">{errors.loco_class}</span>}
            </div>
            <div className="cfg-field">
              <label>Serial No. <span className="cfg-req">*</span></label>
              <input value={form.serial_no} onChange={e => sf('serial_no', e.target.value)} placeholder="e.g. 31001" />
              {errors.serial_no && <span className="cfg-err">{errors.serial_no}</span>}
            </div>
            <div className="cfg-field">
              <label>Config Version <span className="cfg-req">*</span></label>
              <input value={form.config_version} onChange={e => sf('config_version', e.target.value)} placeholder="v3.2" />
              {errors.config_version && <span className="cfg-err">{errors.config_version}</span>}
            </div>
            <div className="cfg-field">
              <label>ECN Reference</label>
              <input value={form.ecn_ref} onChange={e => sf('ecn_ref', e.target.value)} placeholder="CLW/ECN/2026/0001" />
            </div>
            <div className="cfg-field">
              <label>Effective Date</label>
              <input type="date" value={form.effective_date} onChange={e => sf('effective_date', e.target.value)} />
            </div>
            <div className="cfg-field">
              <label>Changed By</label>
              <input value={form.changed_by} onChange={e => sf('changed_by', e.target.value)} placeholder="CLW Engineering / RDSO" />
            </div>
            <div className="cfg-field">
              <label>Status</label>
              <select value={form.status} onChange={e => sf('status', e.target.value)}>
                <option value="PENDING">Pending</option>
                <option value="APPROVED">Approved</option>
                <option value="SUPERSEDED">Superseded</option>
                <option value="REJECTED">Rejected</option>
              </select>
            </div>
            <div className="cfg-field">
              <label>Remarks</label>
              <input value={form.remarks} onChange={e => sf('remarks', e.target.value)} />
            </div>
          </div>
        </div>
        <div className="cfg-modal-footer">
          <_Btn variant="secondary" onClick={onClose} disabled={saving}>Cancel</_Btn>
          <_Btn variant="primary" onClick={handleSave} loading={saving}>
            {isEdit ? '💾 Save Changes' : '➕ Create Config'}
          </_Btn>
        </div>
      </div>
    </div>
  );
}

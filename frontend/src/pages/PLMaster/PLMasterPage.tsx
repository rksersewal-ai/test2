// =============================================================================
// FILE: frontend/src/pages/PLMaster/PLMasterPage.tsx
// Tabbed PL Master module: PL Items | Drawings | Specifications | Alterations
// =============================================================================
import React, { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { PageHeader, Btn, SearchBar, ConfirmDialog, Toast } from '../../components/common';
import type { ToastMsg } from '../../components/common';
import { plMasterService } from '../../services/plMasterService';
import './PLMasterPage.css';

type Tab = 'pl' | 'drawings' | 'specs' | 'alterations';

// ─────────────────────────────────────────────────────────────────────────────
export default function PLMasterPage() {
  const [tab, setTab] = useState<Tab>('pl');
  return (
    <div className="plm-page">
      <PageHeader title="PL Master" subtitle="Part List master data — drawings, specs, BOM, alterations" />
      <div className="plm-tabs">
        {([['pl','PL Items'],['drawings','Drawings'],['specs','Specifications'],['alterations','Alterations']] as [Tab,string][]).map(([t,label]) => (
          <button key={t} className={`plm-tab${tab===t?' plm-tab--active':''}`} onClick={() => setTab(t)}>{label}</button>
        ))}
      </div>
      <div className="plm-body">
        {tab === 'pl'          && <PLItemsTab />}
        {tab === 'drawings'    && <DrawingsTab />}
        {tab === 'specs'       && <SpecsTab />}
        {tab === 'alterations' && <AlterationsTab />}
      </div>
    </div>
  );
}

// ─────────────────────────────────────────────────────────────────────────────
// PL Items Tab
// ─────────────────────────────────────────────────────────────────────────────
function PLItemsTab() {
  const navigate = useNavigate();
  const [items,   setItems]   = useState<any[]>([]);
  const [total,   setTotal]   = useState(0);
  const [page,    setPage]    = useState(1);
  const [search,  setSearch]  = useState('');
  const [loading, setLoading] = useState(false);
  const [toast,   setToast]   = useState<ToastMsg|null>(null);
  const [confirm, setConfirm] = useState<{pl_number:string}|null>(null);
  const [filters, setFilters] = useState({ safety_item:'', inspection_category:'' });

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const p: Record<string,string> = { page: String(page), page_size: '20' };
      if (search) p.q = search;
      if (filters.safety_item) p.safety_item = filters.safety_item;
      if (filters.inspection_category) p.inspection_category = filters.inspection_category;
      const data = await plMasterService.listPL(p);
      setItems(data.results ?? []);
      setTotal(data.total_count ?? 0);
    } catch { setToast({ type:'error', text:'Failed to load PL items.' }); }
    finally { setLoading(false); }
  }, [page, search, filters]);

  useEffect(() => { load(); }, [load]);

  const handleDelete = async () => {
    if (!confirm) return;
    try {
      await plMasterService.deletePL(confirm.pl_number);
      setToast({ type:'success', text:`PL ${confirm.pl_number} deactivated.` });
      load();
    } catch { setToast({ type:'error', text:'Delete failed.' }); }
    finally { setConfirm(null); }
  };

  const totalPages = Math.ceil(total / 20);

  return (
    <div>
      <Toast msg={toast} onClose={() => setToast(null)} />
      <ConfirmDialog
        open={!!confirm}
        title="Deactivate PL Item"
        message={`Deactivate PL number "${confirm?.pl_number}"? It will be hidden from all lists.`}
        confirmLabel="Deactivate"
        onConfirm={handleDelete}
        onCancel={() => setConfirm(null)}
      />

      {/* Toolbar */}
      <div className="plm-toolbar">
        <SearchBar value={search} onChange={v => { setSearch(v); setPage(1); }} placeholder="Search PL number, description, UVAM…" width={320} />
        <select value={filters.inspection_category} onChange={e => setFilters(f => ({...f, inspection_category: e.target.value}))}>
          <option value="">All Categories</option>
          <option value="A">A — Safety Critical</option>
          <option value="B">B — Important</option>
          <option value="C">C — Normal</option>
        </select>
        <select value={filters.safety_item} onChange={e => setFilters(f => ({...f, safety_item: e.target.value}))}>
          <option value="">Safety: All</option>
          <option value="true">Safety Items Only</option>
          <option value="false">Non-Safety</option>
        </select>
        <Btn size="sm" onClick={load} variant="ghost">↺ Refresh</Btn>
        <Btn size="sm" onClick={() => navigate('/pl-master/new')}>+ Add PL Item</Btn>
      </div>

      {/* Table */}
      <div className="plm-table-wrap">
        <table className="plm-table">
          <thead><tr>
            <th>PL Number</th><th>Description</th><th>UVAM ID</th>
            <th>Category</th><th>Safety</th><th>Loco Types</th><th>Actions</th>
          </tr></thead>
          <tbody>
            {loading && <tr><td colSpan={7} className="plm-center plm-muted">Loading…</td></tr>}
            {!loading && items.length === 0 && <tr><td colSpan={7} className="plm-center plm-muted">No PL items found.</td></tr>}
            {items.map(pl => (
              <tr key={pl.pl_number}>
                <td><strong className="plm-mono">{pl.pl_number}</strong></td>
                <td className="plm-desc">{pl.description ?? '—'}</td>
                <td className="plm-mono">{pl.uvam_id ?? '—'}</td>
                <td>{pl.inspection_category
                  ? <span className={`plm-badge plm-badge-cat-${pl.inspection_category?.toLowerCase()}`}>{pl.inspection_category}</span>
                  : '—'}</td>
                <td className="plm-center">{pl.safety_item ? <span className="plm-badge plm-badge-red">✓</span> : '—'}</td>
                <td className="plm-muted" style={{fontSize:11}}>{(pl.loco_types ?? []).join(', ') || '—'}</td>
                <td className="plm-actions">
                  <Btn size="sm" variant="ghost" onClick={() => navigate(`/pl-master/${pl.pl_number}`)}>👁 View</Btn>
                  <Btn size="sm" variant="secondary" onClick={() => navigate(`/pl-master/${pl.pl_number}/edit`)}>✏️ Edit</Btn>
                  <Btn size="sm" variant="danger" onClick={() => setConfirm({ pl_number: pl.pl_number })}>🗑</Btn>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Pagination */}
      <div className="plm-pagination">
        <span className="plm-muted">Showing {items.length} of {total} PL items</span>
        <div className="plm-page-btns">
          <Btn size="sm" variant="secondary" disabled={page <= 1} onClick={() => setPage(p => p - 1)}>← Prev</Btn>
          <span>Page {page} / {totalPages || 1}</span>
          <Btn size="sm" variant="secondary" disabled={page >= totalPages} onClick={() => setPage(p => p + 1)}>Next →</Btn>
        </div>
      </div>
    </div>
  );
}

// ─────────────────────────────────────────────────────────────────────────────
// Drawings Tab
// ─────────────────────────────────────────────────────────────────────────────
function DrawingsTab() {
  const navigate = useNavigate();
  const [items,   setItems]   = useState<any[]>([]);
  const [total,   setTotal]   = useState(0);
  const [page,    setPage]    = useState(1);
  const [search,  setSearch]  = useState('');
  const [loading, setLoading] = useState(false);
  const [toast,   setToast]   = useState<ToastMsg|null>(null);
  const [typeFilter, setTypeFilter] = useState('');

  const DRAWING_TYPES = ['GA','LAYOUT','CIRCUIT','WIRING','ASSEMBLY','DETAIL','ERECTION',
    'INSTALLATION','OVERHAUL','TESTING','SCHEMATIC','PROCESS','VENDOR','OTHER'];

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const p: Record<string,string> = { page: String(page), page_size: '20' };
      if (search) p.q = search;
      if (typeFilter) p.drawing_type = typeFilter;
      const data = await plMasterService.listDrawings(p);
      setItems(data.results ?? []);
      setTotal(data.total_count ?? 0);
    } catch { setToast({ type:'error', text:'Failed to load drawings.' }); }
    finally { setLoading(false); }
  }, [page, search, typeFilter]);

  useEffect(() => { load(); }, [load]);

  const totalPages = Math.ceil(total / 20);

  return (
    <div>
      <Toast msg={toast} onClose={() => setToast(null)} />
      <div className="plm-toolbar">
        <SearchBar value={search} onChange={v => { setSearch(v); setPage(1); }} placeholder="Search drawing number, title…" width={300} />
        <select value={typeFilter} onChange={e => { setTypeFilter(e.target.value); setPage(1); }}>
          <option value="">All Types</option>
          {DRAWING_TYPES.map(t => <option key={t} value={t}>{t}</option>)}
        </select>
        <Btn size="sm" variant="ghost" onClick={load}>↺ Refresh</Btn>
        <Btn size="sm" onClick={() => navigate('/pl-master/drawings/new')}>+ Add Drawing</Btn>
      </div>

      <div className="plm-table-wrap">
        <table className="plm-table">
          <thead><tr>
            <th>Drawing Number</th><th>Title</th><th>Type</th>
            <th>Alteration</th><th>Agency</th><th>Readable</th><th>Actions</th>
          </tr></thead>
          <tbody>
            {loading && <tr><td colSpan={7} className="plm-center plm-muted">Loading…</td></tr>}
            {!loading && items.length === 0 && <tr><td colSpan={7} className="plm-center plm-muted">No drawings found.</td></tr>}
            {items.map(d => (
              <tr key={d.drawing_number}>
                <td><strong className="plm-mono">{d.drawing_number}</strong></td>
                <td className="plm-desc">{d.drawing_title ?? '—'}</td>
                <td><span className="plm-badge plm-badge-blue">{d.drawing_type}</span></td>
                <td className="plm-mono">{d.current_alteration ?? '—'}</td>
                <td className="plm-muted">{d.controlling_agency_name ?? '—'}</td>
                <td className="plm-center">{d.drawing_readable === 'Y' ? '✅' : d.drawing_readable === 'N' ? '❌' : '—'}</td>
                <td className="plm-actions">
                  <Btn size="sm" variant="secondary" onClick={() => navigate(`/pl-master/drawings/${d.drawing_number}/edit`)}>✏️ Edit</Btn>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div className="plm-pagination">
        <span className="plm-muted">{total} drawings</span>
        <div className="plm-page-btns">
          <Btn size="sm" variant="secondary" disabled={page<=1} onClick={() => setPage(p=>p-1)}>← Prev</Btn>
          <span>Page {page} / {totalPages||1}</span>
          <Btn size="sm" variant="secondary" disabled={page>=totalPages} onClick={() => setPage(p=>p+1)}>Next →</Btn>
        </div>
      </div>
    </div>
  );
}

// ─────────────────────────────────────────────────────────────────────────────
// Specifications Tab
// ─────────────────────────────────────────────────────────────────────────────
function SpecsTab() {
  const navigate = useNavigate();
  const [items,   setItems]   = useState<any[]>([]);
  const [total,   setTotal]   = useState(0);
  const [page,    setPage]    = useState(1);
  const [search,  setSearch]  = useState('');
  const [loading, setLoading] = useState(false);
  const [toast,   setToast]   = useState<ToastMsg|null>(null);
  const [typeFilter, setTypeFilter] = useState('');

  const SPEC_TYPES = ['IRS','RDSO','IS','BIS','DIN','EN','ISO','ASTM','AWS','ABB','SIEMENS','OTHER'];

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const p: Record<string,string> = { page: String(page), page_size: '20' };
      if (search) p.q = search;
      if (typeFilter) p.spec_type = typeFilter;
      const data = await plMasterService.listSpecs(p);
      setItems(data.results ?? []);
      setTotal(data.total_count ?? 0);
    } catch { setToast({ type:'error', text:'Failed to load specifications.' }); }
    finally { setLoading(false); }
  }, [page, search, typeFilter]);

  useEffect(() => { load(); }, [load]);

  const totalPages = Math.ceil(total / 20);

  return (
    <div>
      <Toast msg={toast} onClose={() => setToast(null)} />
      <div className="plm-toolbar">
        <SearchBar value={search} onChange={v => { setSearch(v); setPage(1); }} placeholder="Search spec number, title…" width={300} />
        <select value={typeFilter} onChange={e => { setTypeFilter(e.target.value); setPage(1); }}>
          <option value="">All Types</option>
          {SPEC_TYPES.map(t => <option key={t} value={t}>{t}</option>)}
        </select>
        <Btn size="sm" variant="ghost" onClick={load}>↺ Refresh</Btn>
        <Btn size="sm" onClick={() => navigate('/pl-master/specs/new')}>+ Add Spec</Btn>
      </div>

      <div className="plm-table-wrap">
        <table className="plm-table">
          <thead><tr>
            <th>Spec Number</th><th>Title</th><th>Type</th>
            <th>Alteration</th><th>Agency</th><th>Actions</th>
          </tr></thead>
          <tbody>
            {loading && <tr><td colSpan={6} className="plm-center plm-muted">Loading…</td></tr>}
            {!loading && items.length === 0 && <tr><td colSpan={6} className="plm-center plm-muted">No specifications found.</td></tr>}
            {items.map(s => (
              <tr key={s.spec_number}>
                <td><strong className="plm-mono">{s.spec_number}</strong></td>
                <td className="plm-desc">{s.spec_title ?? '—'}</td>
                <td><span className="plm-badge plm-badge-teal">{s.spec_type}</span></td>
                <td className="plm-mono">{s.current_alteration ?? '—'}</td>
                <td className="plm-muted">{s.controlling_agency_name ?? '—'}</td>
                <td className="plm-actions">
                  <Btn size="sm" variant="secondary" onClick={() => navigate(`/pl-master/specs/${s.spec_number}/edit`)}>✏️ Edit</Btn>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div className="plm-pagination">
        <span className="plm-muted">{total} specifications</span>
        <div className="plm-page-btns">
          <Btn size="sm" variant="secondary" disabled={page<=1} onClick={() => setPage(p=>p-1)}>← Prev</Btn>
          <span>Page {page} / {totalPages||1}</span>
          <Btn size="sm" variant="secondary" disabled={page>=totalPages} onClick={() => setPage(p=>p+1)}>Next →</Btn>
        </div>
      </div>
    </div>
  );
}

// ─────────────────────────────────────────────────────────────────────────────
// Alterations Tab
// ─────────────────────────────────────────────────────────────────────────────
function AlterationsTab() {
  const [items,   setItems]   = useState<any[]>([]);
  const [total,   setTotal]   = useState(0);
  const [page,    setPage]    = useState(1);
  const [search,  setSearch]  = useState('');
  const [loading, setLoading] = useState(false);
  const [docType, setDocType] = useState('');
  const [toast,   setToast]   = useState<ToastMsg|null>(null);

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const p: Record<string,string> = { page: String(page), page_size: '20' };
      if (search)  p.document_number = search;
      if (docType) p.document_type   = docType;
      const data = await plMasterService.listAlterations(p);
      setItems(data.results ?? []);
      setTotal(data.total_count ?? 0);
    } catch { setToast({ type:'error', text:'Failed to load alteration history.' }); }
    finally { setLoading(false); }
  }, [page, search, docType]);

  useEffect(() => { load(); }, [load]);

  const totalPages = Math.ceil(total / 20);
  const STATUS_COLOR: Record<string,string> = {
    IMPLEMENTED: 'plm-badge-green', PENDING: 'plm-badge-orange', SUPERSEDED: 'plm-badge-red'
  };

  return (
    <div>
      <Toast msg={toast} onClose={() => setToast(null)} />
      <div className="plm-toolbar">
        <SearchBar value={search} onChange={v => { setSearch(v); setPage(1); }} placeholder="Search document number…" width={280} />
        <select value={docType} onChange={e => { setDocType(e.target.value); setPage(1); }}>
          <option value="">All Types</option>
          <option value="DRAWING">Drawing</option>
          <option value="SPECIFICATION">Specification</option>
          <option value="SMI">SMI</option>
          <option value="RDSO">RDSO</option>
        </select>
        <Btn size="sm" variant="ghost" onClick={load}>↺ Refresh</Btn>
      </div>

      <div className="plm-table-wrap">
        <table className="plm-table">
          <thead><tr>
            <th>Document</th><th>Type</th><th>Alt From → To</th>
            <th>Issue Date</th><th>Source</th><th>Status</th><th>Remarks</th>
          </tr></thead>
          <tbody>
            {loading && <tr><td colSpan={7} className="plm-center plm-muted">Loading…</td></tr>}
            {!loading && items.length === 0 && <tr><td colSpan={7} className="plm-center plm-muted">No alteration records found.</td></tr>}
            {items.map((a, i) => (
              <tr key={i}>
                <td className="plm-mono">{a.document_number}</td>
                <td><span className="plm-badge plm-badge-blue">{a.document_type}</span></td>
                <td className="plm-mono">{a.alteration_from ?? '—'} → {a.alteration_to}</td>
                <td className="plm-muted">{a.issue_date ?? '—'}</td>
                <td className="plm-muted">{a.source_agency ?? '—'}</td>
                <td><span className={`plm-badge ${STATUS_COLOR[a.implementation_status] ?? ''}`}>{a.implementation_status}</span></td>
                <td className="plm-muted" style={{maxWidth:180, overflow:'hidden', textOverflow:'ellipsis', whiteSpace:'nowrap'}}>{a.remarks ?? '—'}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div className="plm-pagination">
        <span className="plm-muted">{total} alteration records</span>
        <div className="plm-page-btns">
          <Btn size="sm" variant="secondary" disabled={page<=1} onClick={() => setPage(p=>p-1)}>← Prev</Btn>
          <span>Page {page} / {totalPages||1}</span>
          <Btn size="sm" variant="secondary" disabled={page>=totalPages} onClick={() => setPage(p=>p+1)}>Next →</Btn>
        </div>
      </div>
    </div>
  );
}

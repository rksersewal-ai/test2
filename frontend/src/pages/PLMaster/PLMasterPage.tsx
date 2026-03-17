import React, { useCallback, useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Btn, ConfirmDialog, PageHeader, SearchBar, Toast } from '../../components/common';
import type { ToastMsg } from '../../components/common';
import { plMasterService } from '../../services/plMasterService';
import './PLMasterPage.css';

type Tab = 'pl' | 'drawings' | 'specs' | 'alterations';

const DRAWING_TYPES = ['GA', 'AD', 'CD', 'SD', 'WD', 'PD', 'ID', 'FD', 'TD', 'JD', 'MD', 'RD', 'BD', 'LD'];
const SPEC_TYPES = ['MS', 'PS', 'TS', 'QS', 'ES', 'IS', 'CS', 'WS', 'HS', 'NS', 'AS', 'FS'];

export default function PLMasterPage() {
  const [tab, setTab] = useState<Tab>('pl');

  return (
    <div className="plm-page">
      <PageHeader title="PL Master" subtitle="Part list, drawings, specifications, and alteration history." />
      <div className="plm-tabs">
        {([
          ['pl', 'PL Items'],
          ['drawings', 'Drawings'],
          ['specs', 'Specifications'],
          ['alterations', 'Alterations'],
        ] as [Tab, string][]).map(([key, label]) => (
          <button
            key={key}
            className={`plm-tab${tab === key ? ' plm-tab--active' : ''}`}
            onClick={() => setTab(key)}
          >
            {label}
          </button>
        ))}
      </div>
      <div className="plm-body">
        {tab === 'pl' && <PLItemsTab />}
        {tab === 'drawings' && <DrawingsTab />}
        {tab === 'specs' && <SpecsTab />}
        {tab === 'alterations' && <AlterationsTab />}
      </div>
    </div>
  );
}

function PLItemsTab() {
  const navigate = useNavigate();
  const [items, setItems] = useState<any[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [search, setSearch] = useState('');
  const [inspectionCategory, setInspectionCategory] = useState('');
  const [safetyItem, setSafetyItem] = useState('');
  const [loading, setLoading] = useState(false);
  const [toast, setToast] = useState<ToastMsg | null>(null);
  const [deleteTarget, setDeleteTarget] = useState<string | null>(null);
  const pageSize = 20;

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const params: Record<string, string> = { page: String(page), page_size: String(pageSize) };
      if (search.trim()) params.q = search.trim();
      if (inspectionCategory) params.inspection_category = inspectionCategory;
      if (safetyItem) params.safety_item = safetyItem;
      const data = await plMasterService.listPL(params);
      setItems(data.results ?? []);
      setTotal(data.total_count ?? data.count ?? 0);
    } catch {
      setToast({ type: 'error', text: 'Failed to load PL items.' });
    } finally {
      setLoading(false);
    }
  }, [inspectionCategory, page, safetyItem, search]);

  useEffect(() => {
    void load();
  }, [load]);

  const handleDelete = async () => {
    if (!deleteTarget) return;
    try {
      await plMasterService.deletePL(deleteTarget);
      setToast({ type: 'success', text: `PL ${deleteTarget} deactivated.` });
      await load();
    } catch {
      setToast({ type: 'error', text: 'Failed to deactivate PL item.' });
    } finally {
      setDeleteTarget(null);
    }
  };

  const totalPages = Math.max(1, Math.ceil(total / pageSize));

  return (
    <div>
      <Toast msg={toast} onClose={() => setToast(null)} />
      <ConfirmDialog
        open={!!deleteTarget}
        title="Deactivate PL Item"
        message={`Deactivate PL number "${deleteTarget ?? ''}"?`}
        confirmLabel="Deactivate"
        onConfirm={handleDelete}
        onCancel={() => setDeleteTarget(null)}
      />

      <div className="plm-toolbar">
        <SearchBar
          value={search}
          onChange={value => {
            setSearch(value);
            setPage(1);
          }}
          placeholder="Search PL number, description, or UVAM ID..."
          width={320}
        />
        <select value={inspectionCategory} onChange={event => { setInspectionCategory(event.target.value); setPage(1); }}>
          <option value="">All Categories</option>
          <option value="CAT-A">CAT-A</option>
          <option value="CAT-B">CAT-B</option>
          <option value="CAT-C">CAT-C</option>
          <option value="CAT-D">CAT-D</option>
        </select>
        <select value={safetyItem} onChange={event => { setSafetyItem(event.target.value); setPage(1); }}>
          <option value="">Safety: All</option>
          <option value="true">Safety Items Only</option>
          <option value="false">Non-Safety</option>
        </select>
        <Btn size="sm" variant="ghost" onClick={() => void load()}>Refresh</Btn>
        <Btn size="sm" onClick={() => navigate('/pl-master/new')}>Add PL Item</Btn>
      </div>

      <div className="plm-table-wrap">
        <table className="plm-table">
          <thead>
            <tr>
              <th>PL Number</th>
              <th>Description</th>
              <th>UVAM ID</th>
              <th>Category</th>
              <th>Safety</th>
              <th>Loco Types</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {loading && (
              <tr>
                <td colSpan={7} className="plm-center plm-muted">Loading...</td>
              </tr>
            )}
            {!loading && items.length === 0 && (
              <tr>
                <td colSpan={7} className="plm-center plm-muted">No PL items found.</td>
              </tr>
            )}
            {items.map(item => (
              <tr key={item.pl_number}>
                <td><strong className="plm-mono">{item.pl_number}</strong></td>
                <td className="plm-desc">{item.description ?? item.part_description ?? '-'}</td>
                <td className="plm-mono">{item.uvam_id ?? '-'}</td>
                <td>{item.inspection_category ?? '-'}</td>
                <td className="plm-center">{item.safety_item ? 'Yes' : '-'}</td>
                <td className="plm-muted" style={{ fontSize: 11 }}>{(item.loco_types ?? item.used_in ?? []).join(', ') || '-'}</td>
                <td className="plm-actions">
                  <Btn size="sm" variant="ghost" onClick={() => navigate(`/pl-master/${item.pl_number}`)}>View</Btn>
                  <Btn size="sm" variant="secondary" onClick={() => navigate(`/pl-master/${item.pl_number}/edit`)}>Edit</Btn>
                  <Btn size="sm" variant="danger" onClick={() => setDeleteTarget(item.pl_number)}>Delete</Btn>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div className="plm-pagination">
        <span className="plm-muted">Showing {items.length} of {total} PL items</span>
        <div className="plm-page-btns">
          <Btn size="sm" variant="secondary" disabled={page <= 1} onClick={() => setPage(current => current - 1)}>Prev</Btn>
          <span>Page {page} / {totalPages}</span>
          <Btn size="sm" variant="secondary" disabled={page >= totalPages} onClick={() => setPage(current => current + 1)}>Next</Btn>
        </div>
      </div>
    </div>
  );
}

function DrawingsTab() {
  const navigate = useNavigate();
  const [items, setItems] = useState<any[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [search, setSearch] = useState('');
  const [drawingType, setDrawingType] = useState('');
  const [loading, setLoading] = useState(false);
  const [toast, setToast] = useState<ToastMsg | null>(null);
  const pageSize = 20;

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const params: Record<string, string> = { page: String(page), page_size: String(pageSize) };
      if (search.trim()) params.q = search.trim();
      if (drawingType) params.drawing_type = drawingType;
      const data = await plMasterService.listDrawings(params);
      setItems(data.results ?? []);
      setTotal(data.total_count ?? data.count ?? 0);
    } catch {
      setToast({ type: 'error', text: 'Failed to load drawings.' });
    } finally {
      setLoading(false);
    }
  }, [drawingType, page, search]);

  useEffect(() => {
    void load();
  }, [load]);

  const totalPages = Math.max(1, Math.ceil(total / pageSize));

  return (
    <div>
      <Toast msg={toast} onClose={() => setToast(null)} />
      <div className="plm-toolbar">
        <SearchBar
          value={search}
          onChange={value => {
            setSearch(value);
            setPage(1);
          }}
          placeholder="Search drawing number or title..."
          width={320}
        />
        <select value={drawingType} onChange={event => { setDrawingType(event.target.value); setPage(1); }}>
          <option value="">All Types</option>
          {DRAWING_TYPES.map(type => (
            <option key={type} value={type}>{type}</option>
          ))}
        </select>
        <Btn size="sm" variant="ghost" onClick={() => void load()}>Refresh</Btn>
        <Btn size="sm" onClick={() => navigate('/pl-master/drawings/new')}>Add Drawing</Btn>
      </div>

      <div className="plm-table-wrap">
        <table className="plm-table">
          <thead>
            <tr>
              <th>Drawing Number</th>
              <th>Title</th>
              <th>Type</th>
              <th>Alteration</th>
              <th>Agency</th>
              <th>Readable</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {loading && (
              <tr>
                <td colSpan={7} className="plm-center plm-muted">Loading...</td>
              </tr>
            )}
            {!loading && items.length === 0 && (
              <tr>
                <td colSpan={7} className="plm-center plm-muted">No drawings found.</td>
              </tr>
            )}
            {items.map(item => (
              <tr key={item.drawing_number}>
                <td><strong className="plm-mono">{item.drawing_number}</strong></td>
                <td className="plm-desc">{item.drawing_title ?? '-'}</td>
                <td>{item.drawing_type ?? '-'}</td>
                <td className="plm-mono">{item.current_alteration ?? '-'}</td>
                <td className="plm-muted">{item.controlling_agency_name ?? '-'}</td>
                <td className="plm-muted">{String(item.drawing_readable ?? '').replace('_', ' ') || '-'}</td>
                <td className="plm-actions">
                  <Btn size="sm" variant="secondary" onClick={() => navigate(`/pl-master/drawings/${item.drawing_number}/edit`)}>Edit</Btn>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div className="plm-pagination">
        <span className="plm-muted">{total} drawings</span>
        <div className="plm-page-btns">
          <Btn size="sm" variant="secondary" disabled={page <= 1} onClick={() => setPage(current => current - 1)}>Prev</Btn>
          <span>Page {page} / {totalPages}</span>
          <Btn size="sm" variant="secondary" disabled={page >= totalPages} onClick={() => setPage(current => current + 1)}>Next</Btn>
        </div>
      </div>
    </div>
  );
}

function SpecsTab() {
  const navigate = useNavigate();
  const [items, setItems] = useState<any[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [search, setSearch] = useState('');
  const [specType, setSpecType] = useState('');
  const [loading, setLoading] = useState(false);
  const [toast, setToast] = useState<ToastMsg | null>(null);
  const pageSize = 20;

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const params: Record<string, string> = { page: String(page), page_size: String(pageSize) };
      if (search.trim()) params.q = search.trim();
      if (specType) params.spec_type = specType;
      const data = await plMasterService.listSpecs(params);
      setItems(data.results ?? []);
      setTotal(data.total_count ?? data.count ?? 0);
    } catch {
      setToast({ type: 'error', text: 'Failed to load specifications.' });
    } finally {
      setLoading(false);
    }
  }, [page, search, specType]);

  useEffect(() => {
    void load();
  }, [load]);

  const totalPages = Math.max(1, Math.ceil(total / pageSize));

  return (
    <div>
      <Toast msg={toast} onClose={() => setToast(null)} />
      <div className="plm-toolbar">
        <SearchBar
          value={search}
          onChange={value => {
            setSearch(value);
            setPage(1);
          }}
          placeholder="Search specification number or title..."
          width={320}
        />
        <select value={specType} onChange={event => { setSpecType(event.target.value); setPage(1); }}>
          <option value="">All Types</option>
          {SPEC_TYPES.map(type => (
            <option key={type} value={type}>{type}</option>
          ))}
        </select>
        <Btn size="sm" variant="ghost" onClick={() => void load()}>Refresh</Btn>
        <Btn size="sm" onClick={() => navigate('/pl-master/specs/new')}>Add Spec</Btn>
      </div>

      <div className="plm-table-wrap">
        <table className="plm-table">
          <thead>
            <tr>
              <th>Spec Number</th>
              <th>Title</th>
              <th>Type</th>
              <th>Alteration</th>
              <th>Agency</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {loading && (
              <tr>
                <td colSpan={6} className="plm-center plm-muted">Loading...</td>
              </tr>
            )}
            {!loading && items.length === 0 && (
              <tr>
                <td colSpan={6} className="plm-center plm-muted">No specifications found.</td>
              </tr>
            )}
            {items.map(item => (
              <tr key={item.spec_number}>
                <td><strong className="plm-mono">{item.spec_number}</strong></td>
                <td className="plm-desc">{item.spec_title ?? '-'}</td>
                <td>{item.spec_type ?? '-'}</td>
                <td className="plm-mono">{item.current_alteration ?? '-'}</td>
                <td className="plm-muted">{item.controlling_agency_name ?? '-'}</td>
                <td className="plm-actions">
                  <Btn size="sm" variant="secondary" onClick={() => navigate(`/pl-master/specs/${item.spec_number}/edit`)}>Edit</Btn>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div className="plm-pagination">
        <span className="plm-muted">{total} specifications</span>
        <div className="plm-page-btns">
          <Btn size="sm" variant="secondary" disabled={page <= 1} onClick={() => setPage(current => current - 1)}>Prev</Btn>
          <span>Page {page} / {totalPages}</span>
          <Btn size="sm" variant="secondary" disabled={page >= totalPages} onClick={() => setPage(current => current + 1)}>Next</Btn>
        </div>
      </div>
    </div>
  );
}

function AlterationsTab() {
  const [items, setItems] = useState<any[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [search, setSearch] = useState('');
  const [documentType, setDocumentType] = useState('');
  const [loading, setLoading] = useState(false);
  const [toast, setToast] = useState<ToastMsg | null>(null);
  const pageSize = 20;

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const params: Record<string, string> = { page: String(page), page_size: String(pageSize) };
      if (search.trim()) params.document_number = search.trim();
      if (documentType) params.document_type = documentType;
      const data = await plMasterService.listAlterations(params);
      setItems(data.results ?? []);
      setTotal(data.total_count ?? data.count ?? 0);
    } catch {
      setToast({ type: 'error', text: 'Failed to load alteration history.' });
    } finally {
      setLoading(false);
    }
  }, [documentType, page, search]);

  useEffect(() => {
    void load();
  }, [load]);

  const totalPages = Math.max(1, Math.ceil(total / pageSize));

  return (
    <div>
      <Toast msg={toast} onClose={() => setToast(null)} />
      <div className="plm-toolbar">
        <SearchBar
          value={search}
          onChange={value => {
            setSearch(value);
            setPage(1);
          }}
          placeholder="Search document number..."
          width={320}
        />
        <select value={documentType} onChange={event => { setDocumentType(event.target.value); setPage(1); }}>
          <option value="">All Types</option>
          <option value="DRAWING">Drawing</option>
          <option value="SPEC">Specification</option>
          <option value="SMI">SMI</option>
          <option value="RDSO">RDSO</option>
        </select>
        <Btn size="sm" variant="ghost" onClick={() => void load()}>Refresh</Btn>
      </div>

      <div className="plm-table-wrap">
        <table className="plm-table">
          <thead>
            <tr>
              <th>Document</th>
              <th>Type</th>
              <th>Alteration</th>
              <th>Date</th>
              <th>Status</th>
              <th>Source</th>
              <th>Remarks</th>
            </tr>
          </thead>
          <tbody>
            {loading && (
              <tr>
                <td colSpan={7} className="plm-center plm-muted">Loading...</td>
              </tr>
            )}
            {!loading && items.length === 0 && (
              <tr>
                <td colSpan={7} className="plm-center plm-muted">No alteration records found.</td>
              </tr>
            )}
            {items.map((item, index) => (
              <tr key={`${item.document_number}-${index}`}>
                <td className="plm-mono">{item.document_number}</td>
                <td>{item.document_type}</td>
                <td className="plm-mono">{item.previous_alteration ?? '-'} to {item.alteration_number ?? '-'}</td>
                <td className="plm-muted">{item.alteration_date ?? '-'}</td>
                <td>{String(item.implementation_status ?? '').replace('_', ' ') || '-'}</td>
                <td className="plm-muted">{item.source_agency ?? '-'}</td>
                <td className="plm-desc">{item.changes_description ?? item.remarks ?? '-'}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div className="plm-pagination">
        <span className="plm-muted">{total} alteration records</span>
        <div className="plm-page-btns">
          <Btn size="sm" variant="secondary" disabled={page <= 1} onClick={() => setPage(current => current - 1)}>Prev</Btn>
          <span>Page {page} / {totalPages}</span>
          <Btn size="sm" variant="secondary" disabled={page >= totalPages} onClick={() => setPage(current => current + 1)}>Next</Btn>
        </div>
      </div>
    </div>
  );
}

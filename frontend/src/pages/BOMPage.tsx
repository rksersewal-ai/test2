// =============================================================================
// FILE: frontend/src/pages/BOMPage.tsx
// Real-API BOM with expandable PL tree + flat list/search tab
// =============================================================================
import React, { useState, useEffect, useCallback, useRef } from 'react';
import { PageHeader, Btn, SearchBar, Toast } from '../components/common';
import type { ToastMsg } from '../components/common';
import { plMasterService } from '../services/plMasterService';
import './BOMPage.css';

type BOMTab = 'tree' | 'list';

export default function BOMPage() {
  const [tab, setTab] = useState<BOMTab>('tree');
  return (
    <div className="bom-page">
      <PageHeader title="Bill of Materials" subtitle="PL-based BOM tree — expandable hierarchy per loco type" />
      <div className="bom-tabs">
        <button className={`bom-tab${tab==='tree'?' bom-tab--active':''}`} onClick={() => setTab('tree')}>🌲 BOM Tree</button>
        <button className={`bom-tab${tab==='list'?' bom-tab--active':''}`} onClick={() => setTab('list')}>📋 Flat List</button>
      </div>
      <div className="bom-body">
        {tab === 'tree' ? <BOMTree /> : <BOMFlatList />}
      </div>
    </div>
  );
}

// ─── BOM Tree ────────────────────────────────────────────────────────────────
function BOMTree() {
  const [rootPL,   setRootPL]   = useState('');
  const [tree,     setTree]     = useState<any>(null);
  const [loading,  setLoading]  = useState(false);
  const [maxDepth, setMaxDepth] = useState(4);
  const [toast,    setToast]    = useState<ToastMsg|null>(null);

  const loadTree = async () => {
    if (!rootPL.trim()) return;
    setLoading(true); setTree(null);
    try {
      const data = await plMasterService.getBOMTree(rootPL.trim(), maxDepth);
      setTree(data);
    } catch {
      setToast({ type:'error', text:`PL "${rootPL}" not found or no BOM data.` });
    } finally { setLoading(false); }
  };

  return (
    <div className="bom-tree-wrap">
      <Toast msg={toast} onClose={() => setToast(null)} />
      <div className="bom-tree-toolbar">
        <SearchBar
          value={rootPL}
          onChange={setRootPL}
          placeholder="Enter root PL number (e.g. PLW-TM-001)…"
          width={320}
        />
        <select value={maxDepth} onChange={e => setMaxDepth(Number(e.target.value))} className="bom-select">
          {[2,3,4,5,6].map(d => <option key={d} value={d}>Depth {d}</option>)}
        </select>
        <Btn size="sm" onClick={loadTree} loading={loading}>🔍 Load BOM</Btn>
        {tree && <Btn size="sm" variant="ghost" onClick={() => setTree(null)}>✕ Clear</Btn>}
      </div>

      {loading && <div className="bom-loading">Loading BOM tree…</div>}

      {!loading && !tree && (
        <div className="bom-empty">
          <div className="bom-empty-icon">🔩</div>
          <p>Enter a PL number above and click <strong>Load BOM</strong> to view the hierarchy.</p>
          <p className="bom-empty-hint">Tip: Use the Depth selector to control how many levels to expand.</p>
        </div>
      )}

      {tree && (
        <div className="bom-tree-panel">
          <div className="bom-tree-header">
            <span className="bom-tree-root-label">Root: <strong className="bom-mono">{tree.pl_number}</strong></span>
            <span className="bom-tree-count">{countNodes(tree.children)} child items</span>
          </div>
          <div className="bom-tree-scroll">
            {tree.children?.length === 0
              ? <div className="bom-no-children">No child BOM items found for this PL number.</div>
              : tree.children?.map((node: any, i: number) => (
                  <BOMNode key={i} node={node} depth={0} />
                ))}
          </div>
        </div>
      )}
    </div>
  );
}

function countNodes(children: any[]): number {
  if (!children?.length) return 0;
  return children.reduce((acc: number, c: any) => acc + 1 + countNodes(c.children ?? []), 0);
}

function BOMNode({ node, depth }: { node: any; depth: number }) {
  const [open, setOpen] = useState(depth < 1);
  const hasChildren = (node.children ?? []).length > 0;
  const indent = depth * 20;

  return (
    <div>
      <div
        className={`bom-node${depth===0?' bom-node--root':''}`}
        style={{ paddingLeft: 16 + indent }}
        onClick={() => hasChildren && setOpen(o => !o)}
      >
        <span className="bom-node-toggle">
          {hasChildren ? (open ? '▼' : '▶') : '•'}
        </span>
        <span className="bom-node-pl bom-mono">{node.pl_number}</span>
        <span className="bom-node-desc">{node.description ?? '—'}</span>
        {node.qty != null && (
          <span className="bom-node-qty">× {node.qty} {node.unit ?? ''}</span>
        )}
        {node.inspection_category && (
          <span className={`bom-node-cat bom-node-cat-${node.inspection_category?.toLowerCase()}`}>
            {node.inspection_category}
          </span>
        )}
        {node.safety_item && <span className="bom-node-safety">⚠ Safety</span>}
      </div>
      {open && hasChildren && (
        <div className="bom-node-children">
          {node.children.map((child: any, i: number) => (
            <BOMNode key={i} node={child} depth={depth + 1} />
          ))}
        </div>
      )}
    </div>
  );
}

// ─── Flat List ────────────────────────────────────────────────────────────────
function BOMFlatList() {
  const [items,   setItems]   = useState<any[]>([]);
  const [total,   setTotal]   = useState(0);
  const [page,    setPage]    = useState(1);
  const [search,  setSearch]  = useState('');
  const [loading, setLoading] = useState(false);
  const [toast,   setToast]   = useState<ToastMsg|null>(null);
  const [filters, setFilters] = useState({ safety_item: '', inspection_category: '' });
  const PAGE_SIZE = 25;

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const p: Record<string,string> = { page: String(page), page_size: String(PAGE_SIZE) };
      if (search) p.q = search;
      if (filters.safety_item) p.safety_item = filters.safety_item;
      if (filters.inspection_category) p.inspection_category = filters.inspection_category;
      const data = await plMasterService.listPL(p);
      setItems(data.results ?? []);
      setTotal(data.total_count ?? 0);
    } catch { setToast({ type:'error', text:'Failed to load BOM items.' }); }
    finally { setLoading(false); }
  }, [page, search, filters]);

  useEffect(() => { load(); }, [load]);

  const totalPages = Math.ceil(total / PAGE_SIZE);

  return (
    <div>
      <Toast msg={toast} onClose={() => setToast(null)} />
      <div className="bom-list-toolbar">
        <SearchBar value={search} onChange={v => { setSearch(v); setPage(1); }} placeholder="Search PL, description, UVAM…" width={300} />
        <select className="bom-select" value={filters.inspection_category}
          onChange={e => setFilters(f => ({...f, inspection_category: e.target.value}))}>
          <option value="">All Categories</option>
          <option value="A">A — Safety Critical</option>
          <option value="B">B — Important</option>
          <option value="C">C — Normal</option>
        </select>
        <select className="bom-select" value={filters.safety_item}
          onChange={e => setFilters(f => ({...f, safety_item: e.target.value}))}>
          <option value="">Safety: All</option>
          <option value="true">Safety Items</option>
          <option value="false">Non-Safety</option>
        </select>
        <Btn size="sm" variant="ghost" onClick={load}>↺ Refresh</Btn>
      </div>

      <div className="bom-list-table-wrap">
        <table className="bom-table">
          <thead><tr>
            <th>PL Number</th><th>Description</th><th>UVAM ID</th>
            <th>Category</th><th>Safety</th><th>Used In</th><th>App Area</th>
          </tr></thead>
          <tbody>
            {loading && <tr><td colSpan={7} className="bom-center bom-muted">Loading…</td></tr>}
            {!loading && items.length===0 && <tr><td colSpan={7} className="bom-center bom-muted">No items found.</td></tr>}
            {items.map(pl => (
              <tr key={pl.pl_number}>
                <td><strong className="bom-mono">{pl.pl_number}</strong></td>
                <td className="bom-desc">{pl.description ?? '—'}</td>
                <td className="bom-mono bom-muted">{pl.uvam_id ?? '—'}</td>
                <td>{pl.inspection_category
                  ? <span className={`bom-badge bom-cat-${pl.inspection_category?.toLowerCase()}`}>{pl.inspection_category}</span>
                  : '—'}</td>
                <td className="bom-center">{pl.safety_item ? '⚠️' : '—'}</td>
                <td className="bom-muted" style={{fontSize:11}}>{pl.used_in ?? '—'}</td>
                <td className="bom-muted" style={{fontSize:11}}>{pl.application_area ?? '—'}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div className="bom-pagination">
        <span className="bom-muted">{total} PL items total</span>
        <div className="bom-page-btns">
          <Btn size="sm" variant="secondary" disabled={page<=1} onClick={() => setPage(p=>p-1)}>← Prev</Btn>
          <span>Page {page} / {totalPages||1}</span>
          <Btn size="sm" variant="secondary" disabled={page>=totalPages} onClick={() => setPage(p=>p+1)}>Next →</Btn>
        </div>
      </div>
    </div>
  );
}

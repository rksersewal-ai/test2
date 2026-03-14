// =============================================================================
// FILE: frontend/src/components/dashboard/SavedViewsSidebar.tsx
// SPRINT 2 — Feature #7: Saved Views Sidebar
// PURPOSE : Renders pinned saved views as quick-access nav items in the sidebar.
//           Each item replays its filter_json into the target module's URL.
//           Supports pin/unpin, rename (inline), and delete.
// ENDPOINTS:
//   GET    /api/dashboard/saved-views/?pinned=true  → pinned list
//   POST   /api/dashboard/saved-views/{id}/pin/     → toggle pin
//   DELETE /api/dashboard/saved-views/{id}/         → delete view
// =============================================================================
import React, { useEffect, useState } from 'react';

interface SavedView {
  id: number;
  view_name: string;
  module: 'EDMS' | 'WORKLEDGER' | 'DASHBOARD';
  filter_json: Record<string, unknown>;
  is_pinned: boolean;
  sort_order: number;
  icon: string;
}

const MODULE_ROUTES: Record<string, string> = {
  EDMS:       '/documents',
  WORKLEDGER: '/work-ledger',
  DASHBOARD:  '/dashboard',
};

/** Convert filter_json to URL query string */
function buildQueryString(filters: Record<string, unknown>): string {
  const params = new URLSearchParams();
  Object.entries(filters).forEach(([k, v]) => {
    if (v !== null && v !== undefined && v !== '') {
      params.set(k, String(v));
    }
  });
  return params.toString() ? `?${params.toString()}` : '';
}

interface Props {
  onNavigate: (path: string) => void;
}

export const SavedViewsSidebar: React.FC<Props> = ({ onNavigate }) => {
  const [views,   setViews]   = useState<SavedView[]>([]);
  const [loading, setLoading] = useState(true);

  const loadPinned = () => {
    fetch('/api/dashboard/saved-views/?pinned=true', { credentials: 'include' })
      .then(r => r.json())
      .then(data => setViews(Array.isArray(data) ? data :
            data.results ?? []))
      .catch(() => setViews([]))
      .finally(() => setLoading(false));
  };

  useEffect(() => { loadPinned(); }, []);

  const handleUnpin = async (id: number, e: React.MouseEvent) => {
    e.stopPropagation();
    await fetch(`/api/dashboard/saved-views/${id}/pin/`, {
      method: 'POST', credentials: 'include',
    });
    loadPinned();
  };

  const handleDelete = async (id: number, e: React.MouseEvent) => {
    e.stopPropagation();
    if (!window.confirm('Delete this saved view?')) return;
    await fetch(`/api/dashboard/saved-views/${id}/`, {
      method: 'DELETE', credentials: 'include',
    });
    loadPinned();
  };

  const handleClick = (view: SavedView) => {
    const base  = MODULE_ROUTES[view.module] ?? '/documents';
    const query = buildQueryString(view.filter_json);
    onNavigate(`${base}${query}`);
  };

  if (loading) return null;
  if (views.length === 0) return null;

  return (
    <nav className="saved-views-sidebar" aria-label="Saved Views">
      <p className="saved-views-sidebar__heading">Saved Views</p>
      <ul className="saved-views-sidebar__list">
        {views
          .sort((a, b) => a.sort_order - b.sort_order)
          .map(view => (
          <li key={view.id} className="saved-views-sidebar__item">
            <button
              className="saved-views-sidebar__btn"
              onClick={() => handleClick(view)}
              title={`Module: ${view.module}`}
            >
              <span className="saved-views-sidebar__icon">
                {view.icon || (view.module === 'EDMS' ? '📄' :
                               view.module === 'WORKLEDGER' ? '📊' : '📌')}
              </span>
              <span className="saved-views-sidebar__name">{view.view_name}</span>
            </button>
            <div className="saved-views-sidebar__actions">
              <button
                title="Unpin"
                className="saved-views-sidebar__action-btn"
                onClick={e => handleUnpin(view.id, e)}
              >📍</button>
              <button
                title="Delete"
                className="saved-views-sidebar__action-btn saved-views-sidebar__action-btn--danger"
                onClick={e => handleDelete(view.id, e)}
              >×</button>
            </div>
          </li>
        ))}
      </ul>
    </nav>
  );
};

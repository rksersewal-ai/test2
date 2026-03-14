// =============================================================================
// FILE: frontend/src/hooks/useSavedViews.ts
// SPRINT 2 — Feature #7
// PURPOSE : CRUD hook for the current user's saved views.
// =============================================================================
import { useState, useEffect, useCallback } from 'react';

export interface SavedView {
  id: number;
  view_name: string;
  module: 'EDMS' | 'WORKLEDGER' | 'DASHBOARD';
  filter_json: Record<string, unknown>;
  widget_config_json: Record<string, unknown>;
  is_pinned: boolean;
  sort_order: number;
  icon: string;
  created_at: string;
}

interface UseSavedViewsResult {
  views:        SavedView[];
  pinned:       SavedView[];
  loading:      boolean;
  createView:   (payload: Partial<SavedView>) => Promise<void>;
  deleteView:   (id: number)                  => Promise<void>;
  togglePin:    (id: number)                  => Promise<void>;
  reorderViews: (items: {id: number; sort_order: number}[]) => Promise<void>;
  reload:       () => void;
}

export function useSavedViews(module?: string): UseSavedViewsResult {
  const [views,   setViews]   = useState<SavedView[]>([]);
  const [loading, setLoading] = useState(true);
  const [tick,    setTick]    = useState(0);

  const reload = () => setTick(t => t + 1);

  useEffect(() => {
    setLoading(true);
    let url = '/api/dashboard/saved-views/';
    if (module) url += `?module=${module}`;
    fetch(url, { credentials: 'include' })
      .then(r => r.json())
      .then(data => setViews(Array.isArray(data) ? data : data.results ?? []))
      .catch(() => setViews([]))
      .finally(() => setLoading(false));
  }, [module, tick]);

  const createView = useCallback(async (payload: Partial<SavedView>) => {
    await fetch('/api/dashboard/saved-views/', {
      method:      'POST',
      credentials: 'include',
      headers:     { 'Content-Type': 'application/json' },
      body:        JSON.stringify(payload),
    });
    reload();
  }, []);

  const deleteView = useCallback(async (id: number) => {
    await fetch(`/api/dashboard/saved-views/${id}/`, {
      method: 'DELETE', credentials: 'include',
    });
    reload();
  }, []);

  const togglePin = useCallback(async (id: number) => {
    await fetch(`/api/dashboard/saved-views/${id}/pin/`, {
      method: 'POST', credentials: 'include',
    });
    reload();
  }, []);

  const reorderViews = useCallback(async (
    items: {id: number; sort_order: number}[]
  ) => {
    await fetch('/api/dashboard/saved-views/reorder/', {
      method:      'POST',
      credentials: 'include',
      headers:     { 'Content-Type': 'application/json' },
      body:        JSON.stringify({ items }),
    });
    reload();
  }, []);

  return {
    views,
    pinned:  views.filter(v => v.is_pinned).sort((a, b) => a.sort_order - b.sort_order),
    loading,
    createView,
    deleteView,
    togglePin,
    reorderViews,
    reload,
  };
}

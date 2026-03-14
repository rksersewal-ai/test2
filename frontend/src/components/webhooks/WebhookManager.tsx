// =============================================================================
// FILE: frontend/src/components/webhooks/WebhookManager.tsx
// SPRINT 7 — Webhook endpoint management page (admin / section head)
//
// Shows:
//   - List of registered endpoints with status
//   - Create / edit / delete endpoint form
//   - Event subscription multi-select
//   - "Send test ping" button per endpoint
//   - Last 10 deliveries per endpoint (inline expandable)
// =============================================================================
import React, { useState, useEffect, useCallback } from 'react';

const ALL_EVENTS = [
  'document.created', 'document.status_changed',
  'revision.created', 'file.uploaded',
  'approval.submitted', 'approval.approved', 'approval.rejected',
  'share_link.created', 'share_link.revoked', 'sanity.errors_found',
];

interface Endpoint {
  id:              number;
  name:            string;
  url:             string;
  events:          string[];
  is_active:       boolean;
  timeout_seconds: number;
  created_by_name: string;
}

interface Delivery {
  id:              number;
  event_name:      string;
  status:          string;
  attempt_count:   number;
  response_status: number | null;
  delivered_at:    string | null;
  error_message:   string;
}

async function api(url: string, opts: RequestInit = {}) {
  const res = await fetch(url, { credentials: 'include', ...opts });
  return res.json();
}

export const WebhookManager: React.FC = () => {
  const [endpoints,  setEndpoints]  = useState<Endpoint[]>([]);
  const [deliveries, setDeliveries] = useState<Record<number, Delivery[]>>({});
  const [expanded,   setExpanded]   = useState<number | null>(null);
  const [showForm,   setShowForm]   = useState(false);
  const [editId,     setEditId]     = useState<number | null>(null);
  const [loading,    setLoading]    = useState(false);

  // Form state
  const [name,       setName]       = useState('');
  const [url,        setUrl]        = useState('');
  const [selEvents,  setSelEvents]  = useState<string[]>([]);
  const [timeout,    setTimeout_]   = useState(10);

  const load = useCallback(async () => {
    const data = await api('/api/v1/webhooks/endpoints/');
    setEndpoints(Array.isArray(data) ? data : data.results ?? []);
  }, []);

  useEffect(() => { load(); }, [load]);

  const loadDeliveries = async (epId: number) => {
    const data = await api(`/api/v1/webhooks/endpoints/${epId}/deliveries/`);
    setDeliveries(prev => ({ ...prev, [epId]: data }));
    setExpanded(expanded === epId ? null : epId);
  };

  const save = async () => {
    setLoading(true);
    const body = { name, url, events: selEvents, timeout_seconds: timeout };
    if (editId) {
      await api(`/api/v1/webhooks/endpoints/${editId}/`, {
        method:  'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body:    JSON.stringify(body),
      });
    } else {
      await api('/api/v1/webhooks/endpoints/', {
        method:  'POST',
        headers: { 'Content-Type': 'application/json' },
        body:    JSON.stringify(body),
      });
    }
    setShowForm(false); setEditId(null); setName(''); setUrl('');
    setSelEvents([]); setTimeout_(10);
    await load();
    setLoading(false);
  };

  const del = async (id: number) => {
    if (!confirm('Delete this webhook endpoint?')) return;
    await api(`/api/v1/webhooks/endpoints/${id}/`, { method: 'DELETE' });
    await load();
  };

  const testPing = async (id: number) => {
    const res = await api(`/api/v1/webhooks/endpoints/${id}/test/`, { method: 'POST' });
    alert(`Test ping queued (delivery #${res.delivery_id})`);
  };

  const toggleEvent = (ev: string) =>
    setSelEvents(prev =>
      prev.includes(ev) ? prev.filter(e => e !== ev) : [...prev, ev]
    );

  const startEdit = (ep: Endpoint) => {
    setEditId(ep.id); setName(ep.name); setUrl(ep.url);
    setSelEvents(ep.events); setTimeout_(ep.timeout_seconds);
    setShowForm(true);
  };

  const STATUS_ICON: Record<string, string> = {
    SUCCESS: '✅', FAILED: '❌', RETRYING: '⏳',
    PENDING: '⏳', ABANDONED: '⚠️',
  };

  return (
    <div className="webhook-manager">
      <div className="webhook-manager__header">
        <h3>🔔 Webhook Endpoints</h3>
        <button className="btn btn--primary btn--sm"
          onClick={() => { setShowForm(f => !f); setEditId(null); }}>
          {showForm ? 'Cancel' : '+ Add endpoint'}
        </button>
      </div>

      {/* Create / Edit form */}
      {showForm && (
        <div className="webhook-form">
          <h4>{editId ? 'Edit endpoint' : 'New endpoint'}</h4>
          <label>Name <input value={name} onChange={e => setName(e.target.value)} /></label>
          <label>URL  <input value={url}  onChange={e => setUrl(e.target.value)}
            placeholder="https://your-server/hooks/edms" /></label>
          <label>Timeout (s)
            <input type="number" value={timeout} min={1} max={60}
              onChange={e => setTimeout_(Number(e.target.value))} />
          </label>
          <fieldset className="webhook-form__events">
            <legend>Subscribe to events (empty = all)</legend>
            {ALL_EVENTS.map(ev => (
              <label key={ev} className="webhook-form__event-label">
                <input type="checkbox"
                  checked={selEvents.includes(ev)}
                  onChange={() => toggleEvent(ev)} />
                {ev}
              </label>
            ))}
          </fieldset>
          <button className="btn btn--primary btn--sm" onClick={save} disabled={loading}>
            {loading ? 'Saving…' : editId ? 'Update' : 'Create'}
          </button>
        </div>
      )}

      {/* Endpoint list */}
      {endpoints.length === 0 ? (
        <p className="webhook-manager__empty">No endpoints registered.</p>
      ) : (
        <ul className="webhook-list">
          {endpoints.map(ep => (
            <li key={ep.id} className={`webhook-item${
              !ep.is_active ? ' webhook-item--inactive' : ''
            }`}>
              <div className="webhook-item__info">
                <span className="webhook-item__name">{ep.name}</span>
                <span className="webhook-item__url">{ep.url}</span>
                <span className="webhook-item__events">
                  {ep.events.length === 0
                    ? 'All events'
                    : ep.events.join(', ')}
                </span>
              </div>
              <div className="webhook-item__actions">
                <button className="btn btn--ghost btn--xs" onClick={() => testPing(ep.id)}>
                  📡 Test
                </button>
                <button className="btn btn--ghost btn--xs"
                  onClick={() => loadDeliveries(ep.id)}>
                  {expanded === ep.id ? '▲ Hide' : '▼ Deliveries'}
                </button>
                <button className="btn btn--ghost btn--xs" onClick={() => startEdit(ep)}>
                  ✏️ Edit
                </button>
                <button className="btn btn--danger btn--xs" onClick={() => del(ep.id)}>
                  🗑️
                </button>
              </div>

              {/* Delivery log */}
              {expanded === ep.id && (
                <ul className="delivery-log">
                  {(deliveries[ep.id] ?? []).slice(0, 10).map(d => (
                    <li key={d.id} className="delivery-log__item">
                      <span>{STATUS_ICON[d.status] ?? '?'}</span>
                      <span className="delivery-log__event">{d.event_name}</span>
                      <span className="delivery-log__status">{d.status}</span>
                      {d.response_status && (
                        <span className="delivery-log__http">
                          HTTP {d.response_status}
                        </span>
                      )}
                      {d.attempt_count > 1 && (
                        <span className="delivery-log__retries">
                          {d.attempt_count} attempts
                        </span>
                      )}
                      {d.error_message && (
                        <span className="delivery-log__err" title={d.error_message}>
                          ⚠️
                        </span>
                      )}
                    </li>
                  ))}
                  {(deliveries[ep.id] ?? []).length === 0 && (
                    <li className="delivery-log__empty">No deliveries yet.</li>
                  )}
                </ul>
              )}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
};

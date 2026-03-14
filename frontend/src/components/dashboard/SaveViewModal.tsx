// =============================================================================
// FILE: frontend/src/components/dashboard/SaveViewModal.tsx
// SPRINT 2 — Feature #7: Save Current View Modal
// PURPOSE : Modal dialog triggered from DocumentListPage or WorkLedgerPage
//           with a "Save View" button. Captures current URL filters and POSTs
//           them as a new saved view.
// ENDPOINT: POST /api/dashboard/saved-views/
// USAGE:
//   const filters = useFilterParams();  // {status: 'ACTIVE', section: 3}
//   <SaveViewModal module="EDMS" currentFilters={filters} onSaved={reload} />
// =============================================================================
import React, { useState } from 'react';

interface Props {
  module: 'EDMS' | 'WORKLEDGER' | 'DASHBOARD';
  currentFilters: Record<string, unknown>;
  onSaved?: () => void;
  onClose: () => void;
}

export const SaveViewModal: React.FC<Props> = ({
  module, currentFilters, onSaved, onClose,
}) => {
  const [name,     setName]     = useState('');
  const [pin,      setPin]      = useState(true);
  const [icon,     setIcon]     = useState('');
  const [saving,   setSaving]   = useState(false);
  const [error,    setError]    = useState<string | null>(null);
  const [success,  setSuccess]  = useState(false);

  const ICON_OPTIONS = [
    { value: '',       label: 'Default' },
    { value: '📄',    label: '📄 Document' },
    { value: '⭐',      label: '⭐ Star'     },
    { value: '📌',    label: '📌 Pin'      },
    { value: '🔍',    label: '🔍 Search'   },
    { value: '📊',    label: '📊 Chart'    },
    { value: '⚙️',     label: '⚙️ Settings' },
  ];

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!name.trim()) return;
    setSaving(true); setError(null);
    try {
      const res = await fetch('/api/dashboard/saved-views/', {
        method:      'POST',
        credentials: 'include',
        headers:     { 'Content-Type': 'application/json' },
        body:        JSON.stringify({
          view_name:   name.trim(),
          module,
          filter_json: currentFilters,
          is_pinned:   pin,
          icon,
        }),
      });
      if (!res.ok) {
        const data = await res.json();
        throw new Error(JSON.stringify(data));
      }
      setSuccess(true);
      onSaved?.();
      setTimeout(onClose, 800);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="save-view-modal-overlay" role="dialog" aria-modal="true">
      <div className="save-view-modal">
        <button className="save-view-modal__close" onClick={onClose}
          aria-label="Close">×</button>
        <h3 className="save-view-modal__title">Save Current View</h3>
        <p className="save-view-modal__subtitle">
          Module: <strong>{module}</strong> &nbsp;&bull;&nbsp;
          {Object.keys(currentFilters).length} filter(s) active
        </p>

        {success ? (
          <p className="save-view-modal__success">✓ View saved!</p>
        ) : (
          <form onSubmit={handleSave} className="save-view-modal__form">
            <label htmlFor="sv-name">View Name *</label>
            <input
              id="sv-name"
              type="text"
              value={name}
              onChange={e => setName(e.target.value)}
              placeholder="e.g. WAG9 Active Drawings, Open Overdue"
              maxLength={120}
              required
              className="edms-input"
            />

            <label htmlFor="sv-icon">Icon</label>
            <select
              id="sv-icon"
              value={icon}
              onChange={e => setIcon(e.target.value)}
              className="edms-select"
            >
              {ICON_OPTIONS.map(o => (
                <option key={o.value} value={o.value}>{o.label}</option>
              ))}
            </select>

            <label className="save-view-modal__pin-label">
              <input
                type="checkbox"
                checked={pin}
                onChange={e => setPin(e.target.checked)}
              />
              {' '}Pin to sidebar
            </label>

            {error && <p className="edms-error">{error}</p>}

            <div className="save-view-modal__actions">
              <button type="button" onClick={onClose}
                className="edms-btn">Cancel</button>
              <button type="submit" disabled={saving || !name.trim()}
                className="edms-btn edms-btn--primary">
                {saving ? 'Saving…' : 'Save View'}
              </button>
            </div>
          </form>
        )}
      </div>
    </div>
  );
};

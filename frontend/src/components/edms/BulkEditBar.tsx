// =============================================================================
// FILE: frontend/src/components/edms/BulkEditBar.tsx
// SPRINT 3 — Feature #6: Bulk Edit UI
// PURPOSE : Sticky bottom bar that appears when 1+ rows are selected in the
//           DocumentListPage table. Provides bulk status change, section move,
//           and delete actions. Calls /api/edms/documents/bulk-update/ (Sprint 1).
//
// USAGE:
//   const bulk = useBulkEdit();
//   // Pass bulk.selectedIds to table rows for checkbox binding
//   <BulkEditBar
//     selectedIds={bulk.selectedIds}
//     onClear={bulk.clearSelection}
//     onDone={reload}
//   />
// =============================================================================
import React, { useState } from 'react';

interface Props {
  selectedIds: number[];
  onClear:     () => void;
  onDone:      () => void;
}

const STATUS_OPTIONS = [
  { value: 'ACTIVE',     label: 'Active'     },
  { value: 'DRAFT',      label: 'Draft'      },
  { value: 'OBSOLETE',   label: 'Obsolete'   },
  { value: 'SUPERSEDED', label: 'Superseded' },
];

export const BulkEditBar: React.FC<Props> = ({ selectedIds, onClear, onDone }) => {
  const [busy,          setBusy]          = useState(false);
  const [error,         setError]         = useState<string | null>(null);
  const [statusValue,   setStatusValue]   = useState('');

  if (selectedIds.length === 0) return null;

  const postBulk = async (fields: Record<string, unknown>) => {
    setBusy(true); setError(null);
    try {
      const res = await fetch('/api/edms/documents/bulk-update/', {
        method:      'POST',
        credentials: 'include',
        headers:     { 'Content-Type': 'application/json' },
        body:        JSON.stringify({ ids: selectedIds, fields }),
      });
      if (!res.ok) {
        const data = await res.json().catch(() => ({}));
        throw new Error(data.error ?? `HTTP ${res.status}`);
      }
      const data = await res.json();
      onClear();
      onDone();
      return data;
    } catch (e: any) {
      setError(e.message);
    } finally {
      setBusy(false);
    }
  };

  const handleStatusChange = () => {
    if (!statusValue) return;
    postBulk({ status: statusValue }).then(() => setStatusValue(''));
  };

  return (
    <div className="bulk-edit-bar" role="region" aria-label="Bulk actions">
      <span className="bulk-edit-bar__count">
        <strong>{selectedIds.length}</strong> document{selectedIds.length !== 1 ? 's' : ''} selected
      </span>

      {/* Status change */}
      <div className="bulk-edit-bar__group">
        <label htmlFor="bulk-status" className="bulk-edit-bar__label">Set status:</label>
        <select
          id="bulk-status"
          className="edms-select bulk-edit-bar__select"
          value={statusValue}
          onChange={e => setStatusValue(e.target.value)}
          disabled={busy}
        >
          <option value="">Choose…</option>
          {STATUS_OPTIONS.map(o => (
            <option key={o.value} value={o.value}>{o.label}</option>
          ))}
        </select>
        <button
          className="edms-btn edms-btn--sm edms-btn--primary"
          onClick={handleStatusChange}
          disabled={busy || !statusValue}
        >
          Apply
        </button>
      </div>

      {/* Error */}
      {error && (
        <span className="bulk-edit-bar__error" role="alert">{error}</span>
      )}

      {/* Loading indicator */}
      {busy && (
        <span className="bulk-edit-bar__busy" aria-live="polite">Updating…</span>
      )}

      {/* Clear selection */}
      <button
        className="edms-btn edms-btn--sm bulk-edit-bar__clear"
        onClick={onClear}
        disabled={busy}
        aria-label="Clear selection"
      >
        &times; Clear
      </button>
    </div>
  );
};

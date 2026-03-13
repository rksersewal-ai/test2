// =============================================================================
// FILE: frontend/src/components/edms/CorrespondentPanel.tsx
// SPRINT 1 — Feature #14: Correspondent Tracking
// PURPOSE : Sidebar panel on Document detail page showing all linked
//           correspondents (RDSO, CLW, BLW etc.) and allowing engineers
//           to add new links with reference number + date.
// ENDPOINTS:
//   GET  /api/edms/correspondent-links/?document={id}  → existing links
//   GET  /api/edms/correspondents/                     → master list
//   POST /api/edms/correspondent-links/                → create link
//   DELETE /api/edms/correspondent-links/{id}/         → remove link
// =============================================================================
import React, { useEffect, useState } from 'react';

interface Correspondent { id: number; name: string; short_code: string; org_type: string; }
interface CorrespondentLink {
  id: number;
  correspondent: number;
  correspondent_name: string;
  correspondent_short_code: string;
  correspondent_org_type: string;
  reference_number: string;
  reference_date: string | null;
  link_type: string;
  remarks: string;
}

const LINK_TYPES = [
  { value: 'ISSUED_BY',    label: 'Issued By'    },
  { value: 'ADDRESSED_TO', label: 'Addressed To' },
  { value: 'CC',           label: 'CC'           },
  { value: 'APPROVED_BY',  label: 'Approved By'  },
  { value: 'CONSULTED',    label: 'Consulted'    },
];

interface Props { documentId: number; readOnly?: boolean; }

export const CorrespondentPanel: React.FC<Props> = ({ documentId, readOnly = false }) => {
  const [links,          setLinks]          = useState<CorrespondentLink[]>([]);
  const [allCorrs,       setAllCorrs]       = useState<Correspondent[]>([]);
  const [showForm,       setShowForm]       = useState(false);
  const [saving,         setSaving]         = useState(false);
  const [form, setForm]                     = useState({
    correspondent: '', link_type: 'ISSUED_BY', reference_number: '', reference_date: '', remarks: '',
  });

  const loadLinks = () => {
    fetch(`/api/edms/correspondent-links/?document=${documentId}`, { credentials: 'include' })
      .then(r => r.json()).then(setLinks).catch(() => {});
  };

  useEffect(() => {
    loadLinks();
    fetch('/api/edms/correspondents/?active=true', { credentials: 'include' })
      .then(r => r.json()).then(setAllCorrs).catch(() => {});
  }, [documentId]);

  const handleAdd = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!form.correspondent) return;
    setSaving(true);
    try {
      await fetch('/api/edms/correspondent-links/', {
        method:      'POST',
        credentials: 'include',
        headers:     { 'Content-Type': 'application/json' },
        body:        JSON.stringify({ ...form, document: documentId }),
      });
      setForm({ correspondent: '', link_type: 'ISSUED_BY', reference_number: '', reference_date: '', remarks: '' });
      setShowForm(false);
      loadLinks();
    } finally { setSaving(false); }
  };

  const handleRemove = async (linkId: number) => {
    if (!window.confirm('Remove this correspondent link?')) return;
    await fetch(`/api/edms/correspondent-links/${linkId}/`, {
      method: 'DELETE', credentials: 'include',
    });
    loadLinks();
  };

  return (
    <div className="correspondent-panel">
      <div className="correspondent-panel__header">
        <h4>Correspondents</h4>
        {!readOnly && (
          <button className="edms-btn edms-btn--sm" onClick={() => setShowForm(s => !s)}>
            {showForm ? 'Cancel' : '+ Add'}
          </button>
        )}
      </div>

      {showForm && (
        <form className="correspondent-form" onSubmit={handleAdd}>
          <select value={form.correspondent} onChange={e => setForm(f => ({ ...f, correspondent: e.target.value }))} required>
            <option value="">-- Select Organisation --</option>
            {allCorrs.map(c => (
              <option key={c.id} value={c.id}>{c.short_code} — {c.name}</option>
            ))}
          </select>
          <select value={form.link_type} onChange={e => setForm(f => ({ ...f, link_type: e.target.value }))}>
            {LINK_TYPES.map(lt => <option key={lt.value} value={lt.value}>{lt.label}</option>)}
          </select>
          <input type="text" placeholder="Reference No (e.g. RDSO/2024/EL/0047)"
            value={form.reference_number}
            onChange={e => setForm(f => ({ ...f, reference_number: e.target.value }))} />
          <input type="date" value={form.reference_date}
            onChange={e => setForm(f => ({ ...f, reference_date: e.target.value }))} />
          <input type="text" placeholder="Remarks (optional)"
            value={form.remarks}
            onChange={e => setForm(f => ({ ...f, remarks: e.target.value }))} />
          <button type="submit" disabled={saving} className="edms-btn edms-btn--primary">
            {saving ? 'Saving...' : 'Add'}
          </button>
        </form>
      )}

      {links.length === 0 ? (
        <p className="correspondent-panel__empty">No correspondents linked.</p>
      ) : (
        <ul className="correspondent-list">
          {links.map(link => (
            <li key={link.id} className="correspondent-list__item">
              <span className="corr-badge corr-badge--{link.correspondent_org_type.toLowerCase()}">
                {link.correspondent_short_code}
              </span>
              <span className="corr-name">{link.correspondent_name}</span>
              <span className="corr-link-type">{link.link_type.replace('_', ' ')}</span>
              {link.reference_number && (
                <span className="corr-ref">Ref: {link.reference_number}</span>
              )}
              {link.reference_date && (
                <span className="corr-date">{link.reference_date}</span>
              )}
              {!readOnly && (
                <button className="corr-remove" onClick={() => handleRemove(link.id)}
                  title="Remove link">×</button>
              )}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
};

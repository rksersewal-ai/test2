// =============================================================================
// FILE: frontend/src/components/edms/DocumentCustomFields.tsx
// SPRINT 1 — Feature #9: Custom Fields per Document Type
// PURPOSE : Dynamic form that renders admin-defined fields for the document's
//           document_type. Mirrors CategoryDynamicFields.tsx from WorkLedger.
// ENDPOINTS:
//   GET  /api/edms/custom-field-definitions/?document_type={id}  → definitions
//   GET  /api/edms/documents/{id}/custom-fields/                  → current values
//   POST /api/edms/documents/{id}/custom-fields/                  → bulk upsert
// =============================================================================
import React, { useEffect, useState, useCallback } from 'react';

interface FieldDefinition {
  id: number;
  field_name: string;
  field_label: string;
  field_type: 'text' | 'number' | 'date' | 'select' | 'boolean';
  select_options_list: string[];
  is_required: boolean;
  sort_order: number;
}

interface FieldValue {
  definition: number;
  field_value: string;
}

interface Props {
  documentId: number;
  documentTypeId: number | null;
  readOnly?: boolean;
  onSaved?: () => void;
}

export const DocumentCustomFields: React.FC<Props> = ({
  documentId, documentTypeId, readOnly = false, onSaved,
}) => {
  const [definitions, setDefinitions] = useState<FieldDefinition[]>([]);
  const [values,      setValues]      = useState<Record<number, string>>({});
  const [saving,      setSaving]      = useState(false);
  const [error,       setError]       = useState<string | null>(null);

  // Load field definitions for this document type
  useEffect(() => {
    if (!documentTypeId) { setDefinitions([]); return; }
    fetch(`/api/edms/custom-field-definitions/?document_type=${documentTypeId}`, {
      credentials: 'include',
    })
      .then(r => r.json())
      .then((data: FieldDefinition[]) => setDefinitions(
        data.filter(d => d.is_active).sort((a, b) => a.sort_order - b.sort_order)
      ))
      .catch(() => setDefinitions([]));
  }, [documentTypeId]);

  // Load current values for this document
  useEffect(() => {
    if (!documentId) return;
    fetch(`/api/edms/documents/${documentId}/custom-fields/`, { credentials: 'include' })
      .then(r => r.json())
      .then((data: FieldValue[]) => {
        const map: Record<number, string> = {};
        data.forEach(v => { map[v.definition] = v.field_value ?? ''; });
        setValues(map);
      })
      .catch(() => {});
  }, [documentId]);

  const handleChange = useCallback((defId: number, val: string) => {
    setValues(prev => ({ ...prev, [defId]: val }));
  }, []);

  const handleSave = async () => {
    setSaving(true); setError(null);
    try {
      const payload = {
        fields: definitions.map(d => ({
          definition_id: String(d.id),
          field_value:   values[d.id] ?? '',
        })),
      };
      const res = await fetch(`/api/edms/documents/${documentId}/custom-fields/`, {
        method:      'POST',
        credentials: 'include',
        headers:     { 'Content-Type': 'application/json' },
        body:        JSON.stringify(payload),
      });
      if (!res.ok) throw new Error(await res.text());
      onSaved?.();
    } catch (e: any) {
      setError(e.message);
    } finally {
      setSaving(false);
    }
  };

  if (!documentTypeId || definitions.length === 0) return null;

  return (
    <fieldset className="edms-custom-fields">
      <legend>Additional Metadata</legend>

      {definitions.map(def => (
        <div key={def.id} className="edms-field">
          <label htmlFor={`cf-${def.id}`}>
            {def.field_label}{def.is_required && ' *'}
          </label>

          {def.field_type === 'select' ? (
            <select
              id={`cf-${def.id}`}
              value={values[def.id] ?? ''}
              onChange={e => handleChange(def.id, e.target.value)}
              disabled={readOnly}
              className="edms-select"
            >
              <option value="">-- Select --</option>
              {def.select_options_list.map(opt => (
                <option key={opt} value={opt}>{opt}</option>
              ))}
            </select>
          ) : def.field_type === 'boolean' ? (
            <input
              id={`cf-${def.id}`}
              type="checkbox"
              checked={values[def.id] === 'true'}
              onChange={e => handleChange(def.id, e.target.checked ? 'true' : 'false')}
              disabled={readOnly}
            />
          ) : (
            <input
              id={`cf-${def.id}`}
              type={def.field_type === 'number' ? 'number' : def.field_type === 'date' ? 'date' : 'text'}
              value={values[def.id] ?? ''}
              onChange={e => handleChange(def.id, e.target.value)}
              disabled={readOnly}
              className="edms-input"
              required={def.is_required}
            />
          )}
        </div>
      ))}

      {!readOnly && (
        <div className="edms-field-actions">
          {error && <span className="edms-error">{error}</span>}
          <button
            type="button"
            className="edms-btn edms-btn--secondary"
            onClick={handleSave}
            disabled={saving}
          >
            {saving ? 'Saving...' : 'Save Metadata'}
          </button>
        </div>
      )}
    </fieldset>
  );
};

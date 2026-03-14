// =============================================================================
// FILE: frontend/src/hooks/useCustomFields.ts
// SPRINT 1 — Feature #9
// PURPOSE : Hook for fetching custom field definitions and document values.
// =============================================================================
import { useState, useEffect } from 'react';

export interface FieldDefinition {
  id: number;
  field_name: string;
  field_label: string;
  field_type: 'text' | 'number' | 'date' | 'select' | 'boolean';
  select_options_list: string[];
  is_required: boolean;
  sort_order: number;
  is_active: boolean;
}

export interface FieldValue {
  definition: number;
  field_name: string;
  field_label: string;
  field_value: string;
  updated_at: string;
}

interface UseCustomFieldsResult {
  definitions: FieldDefinition[];
  values: Record<number, string>;  // definition_id → current value
  loading: boolean;
  reload: () => void;
}

export function useCustomFields(
  documentId: number,
  documentTypeId: number | null
): UseCustomFieldsResult {
  const [definitions, setDefinitions] = useState<FieldDefinition[]>([]);
  const [values,      setValues]      = useState<Record<number, string>>({});
  const [loading,     setLoading]     = useState(true);
  const [tick,        setTick]        = useState(0);

  const reload = () => setTick(t => t + 1);

  useEffect(() => {
    if (!documentTypeId) { setDefinitions([]); setLoading(false); return; }
    Promise.all([
      fetch(`/api/edms/custom-field-definitions/?document_type=${documentTypeId}`, { credentials: 'include' })
        .then(r => r.json()),
      fetch(`/api/edms/documents/${documentId}/custom-fields/`, { credentials: 'include' })
        .then(r => r.json()),
    ]).then(([defs, vals]: [FieldDefinition[], FieldValue[]]) => {
      setDefinitions(defs.filter(d => d.is_active).sort((a, b) => a.sort_order - b.sort_order));
      const map: Record<number, string> = {};
      vals.forEach(v => { map[v.definition] = v.field_value ?? ''; });
      setValues(map);
    }).catch(() => {})
      .finally(() => setLoading(false));
  }, [documentId, documentTypeId, tick]);

  return { definitions, values, loading, reload };
}

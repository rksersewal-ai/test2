// =============================================================================
// FILE: frontend/src/components/work-ledger/CategoryDynamicFields.tsx
// PURPOSE: Renders additional input fields based on selected work category
// =============================================================================
import React from 'react';

interface DynamicField {
  key: string;
  label: string;
  type?: string;
}

const CATEGORY_FIELDS: Record<string, DynamicField[]> = {
  DRAWING_MODIFICATION_OR_NEW: [
    { key: 'drawing_number', label: 'Drawing Number' },
    { key: 'revision', label: 'Revision' },
    { key: 'reason_for_change', label: 'Reason for Change', type: 'textarea' },
  ],
  SPECIFICATION_MODIFICATION: [
    { key: 'specification_number', label: 'Specification Number' },
    { key: 'revision', label: 'Revision' },
    { key: 'details_of_modification', label: 'Details of Modification', type: 'textarea' },
  ],
  PROTOTYPE_INSPECTION: [
    { key: 'firm_name', label: 'Firm Name' },
    { key: 'inspection_date', label: 'Inspection Date', type: 'date' },
    { key: 'inspection_location', label: 'Inspection Location' },
    { key: 'inspection_result', label: 'Inspection Result' },
  ],
  SHOP_VISIT: [
    { key: 'shop_name', label: 'Shop Name' },
    { key: 'visit_date', label: 'Visit Date', type: 'date' },
    { key: 'purpose', label: 'Purpose', type: 'textarea' },
  ],
  NEW_INNOVATION: [
    { key: 'innovation_title', label: 'Innovation Title' },
    { key: 'innovation_description', label: 'Innovation Description', type: 'textarea' },
    { key: 'impact_benefit', label: 'Impact / Benefit', type: 'textarea' },
  ],
};

interface Props {
  categoryCode: string;
  values: Record<string, string>;
  onChange: (key: string, value: string) => void;
}

export const CategoryDynamicFields: React.FC<Props> = ({ categoryCode, values, onChange }) => {
  const fields = CATEGORY_FIELDS[categoryCode];
  if (!fields || fields.length === 0) return null;

  return (
    <fieldset className="wl-dynamic-fields">
      <legend>Category Details</legend>
      {fields.map((f) => (
        <div key={f.key} className="wl-field">
          <label htmlFor={`df-${f.key}`}>{f.label}</label>
          {f.type === 'textarea' ? (
            <textarea
              id={`df-${f.key}`}
              value={values[f.key] ?? ''}
              onChange={(e) => onChange(f.key, e.target.value)}
              rows={3}
            />
          ) : (
            <input
              id={`df-${f.key}`}
              type={f.type ?? 'text'}
              value={values[f.key] ?? ''}
              onChange={(e) => onChange(f.key, e.target.value)}
            />
          )}
        </div>
      ))}
    </fieldset>
  );
};

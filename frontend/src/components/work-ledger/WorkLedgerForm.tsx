// =============================================================================
// FILE: frontend/src/components/work-ledger/WorkLedgerForm.tsx
// PURPOSE: Main work ledger entry form shell with conditional fields
// =============================================================================
import React, { useEffect, useState } from 'react';
import type { WorkLedgerFormData, WorkCategory } from '../../types/workLedger';
import { CategoryDynamicFields } from './CategoryDynamicFields';
import { workLedgerApi } from '../../services/workLedgerApi';

const EMPTY_FORM: WorkLedgerFormData = {
  received_date: '',
  closed_date: '',
  section: 'Mechanical',
  engineer_id: null,
  officer_id: null,
  status: 'Open',
  pl_number: '',
  drawing_number: '',
  drawing_revision: '',
  specification_number: '',
  specification_revision: '',
  tender_number: '',
  case_number: '',
  eoffice_file_no: '',
  work_category_code: '',
  description: '',
  remarks: '',
  details: [],
};

interface Props {
  initialData?: Partial<WorkLedgerFormData>;
  onSubmit: (data: WorkLedgerFormData) => Promise<void>;
  submitLabel?: string;
}

export const WorkLedgerForm: React.FC<Props> = ({ initialData, onSubmit, submitLabel = 'Save' }) => {
  const [form, setForm] = useState<WorkLedgerFormData>({ ...EMPTY_FORM, ...initialData });
  const [categories, setCategories] = useState<WorkCategory[]>([]);
  const [dynamicValues, setDynamicValues] = useState<Record<string, string>>({});
  const [saving, setSaving] = useState(false);
  const [errors, setErrors] = useState<Record<string, string>>({});

  useEffect(() => {
    workLedgerApi.getCategories().then(setCategories);
  }, []);

  const setField = <K extends keyof WorkLedgerFormData>(key: K, value: WorkLedgerFormData[K]) =>
    setForm((prev) => ({ ...prev, [key]: value }));

  const validate = (): boolean => {
    const errs: Record<string, string> = {};
    if (!form.received_date) errs.received_date = 'Received date is required.';
    if (!form.work_category_code) errs.work_category_code = 'Select a work category.';
    if (!form.description.trim()) errs.description = 'Description is required.';
    if (form.status === 'Closed' && !form.closed_date)
      errs.closed_date = 'Closed date required when status is Closed.';
    if (form.closed_date && form.received_date && form.closed_date < form.received_date)
      errs.closed_date = 'Closed date cannot be before received date.';
    setErrors(errs);
    return Object.keys(errs).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!validate()) return;
    const details = Object.entries(dynamicValues)
      .filter(([, v]) => v)
      .map(([field_name, field_value]) => ({ field_name, field_value }));
    setSaving(true);
    try {
      await onSubmit({ ...form, details });
    } finally {
      setSaving(false);
    }
  };

  return (
    <form className="wl-form" onSubmit={handleSubmit}>
      <h2 className="wl-form__title">WORK LEDGER ENTRY</h2>

      {/* Basic Information */}
      <fieldset className="wl-section">
        <legend>Basic Information</legend>
        <div className="wl-field">
          <label>Received Date *</label>
          <input type="date" value={form.received_date}
            onChange={(e) => setField('received_date', e.target.value)} />
          {errors.received_date && <span className="wl-error">{errors.received_date}</span>}
        </div>
        <div className="wl-field">
          <label>Closed Date</label>
          <input type="date" value={form.closed_date}
            onChange={(e) => setField('closed_date', e.target.value)} />
          {errors.closed_date && <span className="wl-error">{errors.closed_date}</span>}
        </div>
        <div className="wl-field">
          <label>Section *</label>
          <select value={form.section} onChange={(e) => setField('section', e.target.value as any)}>
            <option value="Mechanical">Mechanical</option>
            <option value="Electrical">Electrical</option>
            <option value="General">General</option>
          </select>
        </div>
        <div className="wl-field">
          <label>Work Status *</label>
          <select value={form.status} onChange={(e) => setField('status', e.target.value as any)}>
            <option value="Open">Open</option>
            <option value="Closed">Closed</option>
            <option value="Pending">Pending</option>
          </select>
        </div>
      </fieldset>

      {/* Reference Information */}
      <fieldset className="wl-section">
        <legend>Reference Information</legend>
        {([
          ['pl_number', 'PL Number'],
          ['drawing_number', 'Drawing Number'],
          ['specification_number', 'Specification'],
          ['tender_number', 'Tender No / Case No'],
          ['eoffice_file_no', 'eOffice File No'],
        ] as [keyof WorkLedgerFormData, string][]).map(([key, label]) => (
          <div key={key} className="wl-field">
            <label>{label}</label>
            <input type="text" value={(form[key] as string) ?? ''}
              onChange={(e) => setField(key, e.target.value)} />
          </div>
        ))}
      </fieldset>

      {/* Work Category */}
      <fieldset className="wl-section">
        <legend>Work Category *</legend>
        {errors.work_category_code && <span className="wl-error">{errors.work_category_code}</span>}
        <div className="wl-category-grid">
          {categories.map((cat) => (
            <label key={cat.code} className="wl-checkbox-label">
              <input
                type="radio"
                name="work_category_code"
                value={cat.code}
                checked={form.work_category_code === cat.code}
                onChange={() => {
                  setField('work_category_code', cat.code);
                  setDynamicValues({});
                }}
              />
              {cat.label}
            </label>
          ))}
        </div>
      </fieldset>

      {/* Dynamic Fields */}
      <CategoryDynamicFields
        categoryCode={form.work_category_code}
        values={dynamicValues}
        onChange={(k, v) => setDynamicValues((prev) => ({ ...prev, [k]: v }))}
      />

      {/* Details */}
      <fieldset className="wl-section">
        <legend>Details</legend>
        <div className="wl-field">
          <label>Work Description *</label>
          <textarea rows={4} value={form.description}
            onChange={(e) => setField('description', e.target.value)} />
          {errors.description && <span className="wl-error">{errors.description}</span>}
        </div>
        <div className="wl-field">
          <label>Remarks / Notes</label>
          <textarea rows={3} value={form.remarks ?? ''}
            onChange={(e) => setField('remarks', e.target.value)} />
        </div>
      </fieldset>

      <div className="wl-form__actions">
        <button type="submit" className="wl-btn wl-btn--primary" disabled={saving}>
          {saving ? 'Saving...' : submitLabel}
        </button>
      </div>
    </form>
  );
};

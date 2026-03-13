// =============================================================================
// FILE: frontend/src/components/work-ledger/WorkLedgerFormV2.tsx
// FIX (#16): Removed unused import of workLedgerApi.
// FIX (#11): Section dropdown now calls core/sections API via useSections hook.
// =============================================================================
import React, { useEffect, useState } from 'react';
import type { WorkLedgerFormData } from '../../types/workLedger';
import { DropdownSelect } from '../common/DropdownSelect';
import { DROPDOWN_GROUPS } from '../../types/dropdown';
import { CategoryDynamicFields } from './CategoryDynamicFields';
import { useDropdown } from '../../hooks/useDropdown';
import { dropdownApi } from '../../services/dropdownApi';

const EMPTY_FORM: WorkLedgerFormData = {
  received_date: '',
  closed_date: '',
  section: '',
  engineer_id: null,
  officer_id: null,
  status: 'OPEN',
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

interface Section { id: number; code: string; name: string; }

interface Props {
  initialData?: Partial<WorkLedgerFormData>;
  onSubmit: (data: WorkLedgerFormData) => Promise<void>;
  submitLabel?: string;
}

export const WorkLedgerFormV2: React.FC<Props> = ({
  initialData, onSubmit, submitLabel = 'Save',
}) => {
  const [form, setForm] = useState<WorkLedgerFormData>({ ...EMPTY_FORM, ...initialData });
  const [dynamicValues, setDynamicValues] = useState<Record<string, string>>({});
  const [saving, setSaving] = useState(false);
  const [errors, setErrors] = useState<Record<string, string>>({});

  // FIX (#11): Sections from core API (not dropdown_master)
  const [sections, setSections] = useState<Section[]>([]);
  useEffect(() => {
    dropdownApi.getSections().then(setSections).catch(console.error);
  }, []);

  // Work category items from admin-managed dropdown
  const { items: categoryItems } = useDropdown(DROPDOWN_GROUPS.WORK_CATEGORY);

  const setField = <K extends keyof WorkLedgerFormData>(key: K, value: WorkLedgerFormData[K]) =>
    setForm((prev) => ({ ...prev, [key]: value }));

  const validate = (): boolean => {
    const errs: Record<string, string> = {};
    if (!form.received_date)       errs.received_date       = 'Received date is required.';
    if (!form.section)             errs.section             = 'Section is required.';
    if (!form.work_category_code)  errs.work_category_code  = 'Select a work category.';
    if (!form.description.trim())  errs.description         = 'Description is required.';
    if (form.status === 'CLOSED' && !form.closed_date)
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
    try { await onSubmit({ ...form, details }); }
    finally { setSaving(false); }
  };

  return (
    <form className="wl-form" onSubmit={handleSubmit}>
      <h2 className="wl-form__title">WORK LEDGER ENTRY</h2>

      <fieldset className="wl-section">
        <legend>Basic Information</legend>

        <div className="wl-field">
          <label htmlFor="f-received-date">Received Date *</label>
          <input id="f-received-date" type="date" value={form.received_date}
            onChange={(e) => setField('received_date', e.target.value)} />
          {errors.received_date && <span className="wl-error">{errors.received_date}</span>}
        </div>

        <div className="wl-field">
          <label htmlFor="f-closed-date">Closed Date</label>
          <input id="f-closed-date" type="date" value={form.closed_date}
            onChange={(e) => setField('closed_date', e.target.value)} />
          {errors.closed_date && <span className="wl-error">{errors.closed_date}</span>}
        </div>

        {/* FIX (#11): Section from core_section table */}
        <div className="wl-field">
          <label htmlFor="f-section">Section *</label>
          <select
            id="f-section"
            className="wl-select"
            value={form.section}
            onChange={(e) => setField('section', e.target.value)}
            required
          >
            <option value="">-- Select Section --</option>
            {sections
              .slice()
              .sort((a, b) => a.name.localeCompare(b.name))
              .map((s) => (
                <option key={s.code} value={s.code}>{s.name}</option>
              ))}
          </select>
          {errors.section && <span className="wl-error">{errors.section}</span>}
        </div>

        {/* Work Status from admin dropdown */}
        <div className="wl-field">
          <label htmlFor="f-status">Work Status *</label>
          <DropdownSelect
            id="f-status"
            groupKey={DROPDOWN_GROUPS.WORK_STATUS}
            value={form.status}
            onChange={(code) => setField('status', code as any)}
            required
          />
        </div>
      </fieldset>

      <fieldset className="wl-section">
        <legend>Reference Information</legend>
        {([
          ['pl_number',            'PL Number'],
          ['drawing_number',       'Drawing Number'],
          ['drawing_revision',     'Drawing Revision'],
          ['specification_number', 'Specification No'],
          ['tender_number',        'Tender No / Case No'],
          ['eoffice_file_no',      'eOffice File No'],
        ] as [keyof WorkLedgerFormData, string][]).map(([key, label]) => (
          <div key={key} className="wl-field">
            <label htmlFor={`f-${key}`}>{label}</label>
            <input id={`f-${key}`} type="text" value={(form[key] as string) ?? ''}
              onChange={(e) => setField(key, e.target.value)} />
          </div>
        ))}
      </fieldset>

      <fieldset className="wl-section">
        <legend>Work Category *</legend>
        {errors.work_category_code &&
          <span className="wl-error">{errors.work_category_code}</span>}
        <div className="wl-category-grid">
          {categoryItems.map((cat) => (
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

      <CategoryDynamicFields
        categoryCode={form.work_category_code}
        values={dynamicValues}
        onChange={(k, v) => setDynamicValues((prev) => ({ ...prev, [k]: v }))}
      />

      <fieldset className="wl-section">
        <legend>Details</legend>
        <div className="wl-field">
          <label htmlFor="f-description">Work Description *</label>
          <textarea id="f-description" rows={4} value={form.description}
            onChange={(e) => setField('description', e.target.value)} />
          {errors.description && <span className="wl-error">{errors.description}</span>}
        </div>
        <div className="wl-field">
          <label htmlFor="f-remarks">Remarks / Notes</label>
          <textarea id="f-remarks" rows={3} value={form.remarks ?? ''}
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

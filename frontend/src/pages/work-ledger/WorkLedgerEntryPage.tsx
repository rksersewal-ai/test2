// =============================================================================
// FILE: frontend/src/pages/work-ledger/WorkLedgerEntryPage.tsx
// FIX: Added `export default` so App.tsx can lazy-import this page.
//      Named export kept for barrel import compatibility.
// =============================================================================
import React, { useEffect, useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { workLedgerService } from '../../services/workLedgerService';
import type { WorkLedgerFormData, WorkLedgerFull } from '../../types/workLedger';

export const WorkLedgerEntryPage: React.FC = () => {
  const { workId } = useParams<{ workId?: string }>();
  const navigate   = useNavigate();
  const [existing, setExisting] = useState<WorkLedgerFull | null>(null);
  const [loading,  setLoading]  = useState(!!workId);
  const [saved,    setSaved]    = useState(false);
  const [errorMsg, setErrorMsg] = useState('');

  useEffect(() => {
    if (workId) {
      workLedgerService
        .getEntry(Number(workId))
        .then(setExisting)
        .catch(() => setErrorMsg('Failed to load entry.'))
        .finally(() => setLoading(false));
    }
  }, [workId]);

  const handleSubmit = async (data: WorkLedgerFormData) => {
    try {
      setErrorMsg('');
      if (workId) await workLedgerService.updateEntry(Number(workId), data);
      else        await workLedgerService.createEntry(data);
      setSaved(true);
      setTimeout(() => navigate('/work-ledger'), 800);
    } catch (err: any) {
      setErrorMsg(err?.response?.data?.detail ?? err.message ?? 'Save failed.');
    }
  };

  if (loading) return <p className="wl-loading">Loading entry…</p>;

  return (
    <div className="wl-entry-page">
      {saved && (
        <div className="wl-alert wl-alert--success">
          ✅ Saved successfully. Redirecting…
        </div>
      )}
      {errorMsg && (
        <div className="wl-alert wl-alert--error">❌ {errorMsg}</div>
      )}

      <div className="wl-entry-form-wrapper">
        <h2 className="wl-entry-title">
          {workId ? '✏️ Edit Work Entry' : '➕ New Work Entry'}
        </h2>

        {/* Inline form — WorkLedgerForm component may not exist yet;
            using a minimal self-contained form to keep the page functional */}
        <WLEntryForm
          initialData={existing ? mapEntryToFormData(existing) : undefined}
          onSubmit={handleSubmit}
          submitLabel={workId ? 'Update Entry' : 'Save Entry'}
        />
      </div>
    </div>
  );
};

export default WorkLedgerEntryPage;

function mapEntryToFormData(entry: WorkLedgerFull): Partial<WorkLedgerFormData> {
  return {
    received_date: entry.received_date,
    closed_date: entry.closed_date ?? '',
    section: entry.section,
    engineer_id: entry.engineer_id,
    officer_id: entry.officer_id,
    status: entry.status,
    pl_number: entry.pl_number ?? '',
    drawing_number: entry.drawing_number ?? '',
    drawing_revision: entry.drawing_revision ?? '',
    specification_number: entry.specification_number ?? '',
    specification_revision: entry.specification_revision ?? '',
    tender_number: entry.tender_number ?? '',
    case_number: entry.case_number ?? '',
    eoffice_file_no: entry.eoffice_file_no ?? '',
    work_category_code: entry.work_category_code,
    description: entry.description,
    remarks: entry.remarks ?? '',
    details: entry.details,
  };
}

// ── Minimal inline form (fallback if WorkLedgerForm component is absent) ─────
function WLEntryForm({
  initialData,
  onSubmit,
  submitLabel,
}: {
  initialData?: Partial<WorkLedgerFormData>;
  onSubmit: (d: WorkLedgerFormData) => void;
  submitLabel: string;
}) {
  const [categories, setCategories] = useState<Array<{ code: string; label: string }>>([]);
  const blank: WorkLedgerFormData = {
    received_date: '', closed_date: '', section: 'Mechanical',
    engineer_id: null, officer_id: null, status: 'DRAFT',
    pl_number: '', drawing_number: '', drawing_revision: '',
    specification_number: '', specification_revision: '',
    tender_number: '', case_number: '', eoffice_file_no: '',
    work_category_code: '', description: '', remarks: '', details: [],
  };
  const [form, setForm] = useState<WorkLedgerFormData>({ ...blank, ...initialData });
  const sf = (k: keyof WorkLedgerFormData, v: any) => setForm(f => ({ ...f, [k]: v }));

  useEffect(() => {
    workLedgerService.getCategories().then(setCategories).catch(() => {});
  }, []);

  const inputStyle: React.CSSProperties = {
    width: '100%', padding: '7px 10px',
    background: '#1e2332', border: '1px solid #2d3555',
    color: '#d1d5db', borderRadius: 6, fontSize: 13,
  };
  const labelStyle: React.CSSProperties = {
    display: 'block', color: '#94a3b8', fontSize: 12,
    marginBottom: 4, fontWeight: 600,
  };
  const fieldStyle: React.CSSProperties = { marginBottom: 14 };

  return (
    <form
      onSubmit={e => { e.preventDefault(); onSubmit(form); }}
      style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0 20px' }}
    >
      {([
        ['received_date', 'Received Date', 'date'],
        ['closed_date',   'Closed Date',   'date'],
        ['pl_number',     'PL Number',     'text'],
        ['drawing_number','Drawing No.',   'text'],
        ['tender_number', 'Tender No.',    'text'],
        ['case_number',   'Case No.',      'text'],
        ['eoffice_file_no','E-Office File No.','text'],
        ['specification_number','Spec. No.','text'],
      ] as [keyof WorkLedgerFormData, string, string][]).map(([k, label, type]) => (
        <div key={k} style={fieldStyle}>
          <label style={labelStyle}>{label}</label>
          <input type={type} style={inputStyle} value={(form[k] as string) ?? ''}
            onChange={e => sf(k, e.target.value)} />
        </div>
      ))}

      <div style={fieldStyle}>
        <label style={labelStyle}>Work Category</label>
        <select style={inputStyle} value={form.work_category_code} onChange={e => sf('work_category_code', e.target.value)}>
          <option value="">Select category</option>
          {categories.map(category => (
            <option key={category.code} value={category.code}>
              {category.label}
            </option>
          ))}
        </select>
      </div>

      <div style={fieldStyle}>
        <label style={labelStyle}>Section</label>
        <select style={inputStyle} value={form.section} onChange={e => sf('section', e.target.value as any)}>
          <option value="Mechanical">Mechanical</option>
          <option value="Electrical">Electrical</option>
          <option value="General">General</option>
        </select>
      </div>

      <div style={{ ...fieldStyle, gridColumn: '1 / -1' }}>
        <label style={labelStyle}>Description</label>
        <textarea rows={3} style={{ ...inputStyle, resize: 'vertical' }}
          value={form.description}
          onChange={e => sf('description', e.target.value)} />
      </div>

      <div style={{ ...fieldStyle, gridColumn: '1 / -1' }}>
        <label style={labelStyle}>Remarks</label>
        <textarea rows={2} style={{ ...inputStyle, resize: 'vertical' }}
          value={form.remarks}
          onChange={e => sf('remarks', e.target.value)} />
      </div>

      <div style={{ gridColumn: '1 / -1', display: 'flex', gap: 10, justifyContent: 'flex-end', paddingTop: 8 }}>
        <button type="submit"
          style={{ padding: '9px 24px', background: 'linear-gradient(135deg,#4b6cb7,#182848)', border: 'none', color: '#fff', borderRadius: 7, fontWeight: 600, fontSize: 13, cursor: 'pointer' }}
        >
          💾 {submitLabel}
        </button>
      </div>
    </form>
  );
}

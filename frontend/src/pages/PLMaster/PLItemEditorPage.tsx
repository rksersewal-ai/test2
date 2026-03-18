import React, { useEffect, useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { Btn, PageHeader, Toast } from '../../components/common';
import type { ToastMsg } from '../../components/common';
import { plMasterService } from '../../services/plMasterService';

const SAFETY_CLASSIFICATIONS = ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW'];

export default function PLItemEditorPage() {
  const { plNumber } = useParams<{ plNumber?: string }>();
  const navigate = useNavigate();
  const isEdit = Boolean(plNumber);
  const [agencies, setAgencies] = useState<any[]>([]);
  const [loading, setLoading] = useState(isEdit);
  const [saving, setSaving] = useState(false);
  const [toast, setToast] = useState<ToastMsg | null>(null);
  const [form, setForm] = useState({
    pl_number: '',
    part_description: '',
    inspection_category: '',
    safety_item: false,
    safety_classification: '',
    uvam_id: '',
    application_area: '',
    used_in_text: '',
    controlling_agency: '',
    remarks: '',
    is_active: true,
  });

  useEffect(() => {
    plMasterService.listAgencies().then(setAgencies).catch(() => {});
  }, []);

  useEffect(() => {
    if (!plNumber) return;
    plMasterService.getPL(plNumber)
      .then(data => {
        setForm({
          pl_number: data.pl_number ?? '',
          part_description: data.part_description ?? '',
          inspection_category: data.inspection_category ?? '',
          safety_item: Boolean(data.safety_item),
          safety_classification: data.safety_classification ?? '',
          uvam_id: data.uvam_id ?? '',
          application_area: data.application_area ?? '',
          used_in_text: (data.used_in ?? []).join(', '),
          controlling_agency: data.controlling_agency ?? '',
          remarks: data.remarks ?? '',
          is_active: Boolean(data.is_active),
        });
      })
      .catch(() => {
        setToast({ type: 'error', text: 'Failed to load PL item.' });
      })
      .finally(() => setLoading(false));
  }, [plNumber]);

  const setField = (key: string, value: string | boolean) => {
    setForm(current => ({ ...current, [key]: value }));
  };

  const handleSave = async () => {
    if (!form.pl_number.trim() || !form.part_description.trim()) {
      setToast({ type: 'error', text: 'PL number and description are required.' });
      return;
    }
    if (form.safety_item && !form.safety_classification) {
      setToast({ type: 'error', text: 'Select a safety classification for safety items.' });
      return;
    }

    setSaving(true);
    try {
      const payload = {
        pl_number: form.pl_number.trim(),
        part_description: form.part_description.trim(),
        inspection_category: form.inspection_category || '',
        safety_item: form.safety_item,
        safety_classification: form.safety_item ? form.safety_classification : '',
        uvam_id: form.uvam_id.trim(),
        application_area: form.application_area.trim(),
        used_in: form.used_in_text
          .split(',')
          .map(item => item.trim())
          .filter(Boolean),
        controlling_agency: form.controlling_agency || null,
        remarks: form.remarks.trim(),
        is_active: form.is_active,
      };

      const saved = isEdit
        ? await plMasterService.updatePL(plNumber!, payload)
        : await plMasterService.createPL(payload);

      navigate(`/pl-master/${saved.pl_number ?? payload.pl_number}`);
    } catch {
      setToast({ type: 'error', text: 'Failed to save PL item.' });
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return <div style={{ padding: 24, color: '#94a3b8' }}>Loading...</div>;
  }

  return (
    <div style={{ padding: 24 }}>
      <PageHeader
        title={isEdit ? `Edit ${form.pl_number}` : 'New PL Item'}
        subtitle="Create or update an active PL master record."
      >
        <Btn size="sm" variant="secondary" onClick={() => navigate(isEdit ? `/pl-master/${plNumber}` : '/pl-master')}>Cancel</Btn>
        <Btn size="sm" onClick={() => void handleSave()} loading={saving}>Save</Btn>
      </PageHeader>

      <Toast msg={toast} onClose={() => setToast(null)} />

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16 }}>
        <Field label="PL Number" value={form.pl_number} onChange={value => setField('pl_number', value)} disabled={isEdit} />
        <Field label="UVAM ID" value={form.uvam_id} onChange={value => setField('uvam_id', value)} />
        <Field label="Description" value={form.part_description} onChange={value => setField('part_description', value)} full />
        <Field label="Application Area" value={form.application_area} onChange={value => setField('application_area', value)} />
        <SelectField
          label="Inspection Category"
          value={form.inspection_category}
          onChange={value => setField('inspection_category', value)}
          options={['', 'CAT-A', 'CAT-B', 'CAT-C', 'CAT-D']}
        />
        <SelectField
          label="Safety Classification"
          value={form.safety_classification}
          onChange={value => setField('safety_classification', value)}
          options={SAFETY_CLASSIFICATIONS}
          disabled={!form.safety_item}
        />
        <SelectField
          label="Controlling Agency"
          value={form.controlling_agency}
          onChange={value => setField('controlling_agency', value)}
          options={['', ...agencies.map(agency => agency.agency_code)]}
        />
        <Field label="Loco Types" value={form.used_in_text} onChange={value => setField('used_in_text', value)} placeholder="WAG9, WAP7" full />
        <Field label="Remarks" value={form.remarks} onChange={value => setField('remarks', value)} full />
        <CheckboxField
          label="Safety Item"
          checked={form.safety_item}
          onChange={value => {
            setField('safety_item', value);
            if (!value) {
              setField('safety_classification', '');
            }
          }}
        />
        <CheckboxField label="Active" checked={form.is_active} onChange={value => setField('is_active', value)} />
      </div>
    </div>
  );
}

function Field({
  label,
  value,
  onChange,
  disabled,
  full,
  placeholder,
}: {
  label: string;
  value: string;
  onChange: (value: string) => void;
  disabled?: boolean;
  full?: boolean;
  placeholder?: string;
}) {
  return (
    <label style={{ display: 'grid', gap: 6, gridColumn: full ? '1 / -1' : undefined }}>
      <span style={{ color: '#94a3b8', fontSize: 12, fontWeight: 600 }}>{label}</span>
      <input
        value={value}
        disabled={disabled}
        placeholder={placeholder}
        onChange={event => onChange(event.target.value)}
        style={{
          padding: '10px 12px',
          background: '#1e2332',
          border: '1px solid #2d3555',
          color: '#d1d5db',
          borderRadius: 8,
        }}
      />
    </label>
  );
}

function SelectField({
  label,
  value,
  onChange,
  options,
  disabled,
}: {
  label: string;
  value: string;
  onChange: (value: string) => void;
  options: string[];
  disabled?: boolean;
}) {
  return (
    <label style={{ display: 'grid', gap: 6 }}>
      <span style={{ color: '#94a3b8', fontSize: 12, fontWeight: 600 }}>{label}</span>
      <select
        value={value}
        disabled={disabled}
        onChange={event => onChange(event.target.value)}
        style={{
          padding: '10px 12px',
          background: '#1e2332',
          border: '1px solid #2d3555',
          color: '#d1d5db',
          borderRadius: 8,
        }}
      >
        <option value="">Select...</option>
        {options.filter(Boolean).map(option => (
          <option key={option} value={option}>{option}</option>
        ))}
      </select>
    </label>
  );
}

function CheckboxField({
  label,
  checked,
  onChange,
}: {
  label: string;
  checked: boolean;
  onChange: (value: boolean) => void;
}) {
  return (
    <label style={{ display: 'flex', gap: 10, alignItems: 'center', color: '#d1d5db' }}>
      <input type="checkbox" checked={checked} onChange={event => onChange(event.target.checked)} />
      {label}
    </label>
  );
}

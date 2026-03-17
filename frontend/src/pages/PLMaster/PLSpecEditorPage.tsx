import React, { useEffect, useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { Btn, PageHeader, Toast } from '../../components/common';
import type { ToastMsg } from '../../components/common';
import { plMasterService } from '../../services/plMasterService';

const SPEC_TYPES = ['MS', 'PS', 'TS', 'QS', 'ES', 'IS', 'CS', 'WS', 'HS', 'NS', 'AS', 'FS'];

export default function PLSpecEditorPage() {
  const { specNumber } = useParams<{ specNumber?: string }>();
  const navigate = useNavigate();
  const isEdit = Boolean(specNumber);
  const [agencies, setAgencies] = useState<any[]>([]);
  const [loading, setLoading] = useState(isEdit);
  const [saving, setSaving] = useState(false);
  const [toast, setToast] = useState<ToastMsg | null>(null);
  const [form, setForm] = useState({
    spec_number: '',
    spec_title: '',
    spec_type: '',
    current_alteration: '',
    controlling_agency: '',
    source_reference: '',
    is_active: true,
  });

  useEffect(() => {
    plMasterService.listAgencies().then(setAgencies).catch(() => {});
  }, []);

  useEffect(() => {
    if (!specNumber) return;
    plMasterService.getSpec(specNumber)
      .then(data => {
        setForm({
          spec_number: data.spec_number ?? '',
          spec_title: data.spec_title ?? '',
          spec_type: data.spec_type ?? '',
          current_alteration: data.current_alteration ?? '',
          controlling_agency: data.controlling_agency ?? '',
          source_reference: data.source_reference ?? '',
          is_active: Boolean(data.is_active),
        });
      })
      .catch(() => {
        setToast({ type: 'error', text: 'Failed to load specification.' });
      })
      .finally(() => setLoading(false));
  }, [specNumber]);

  const setField = (key: string, value: string | boolean) => {
    setForm(current => ({ ...current, [key]: value }));
  };

  const handleSave = async () => {
    if (!form.spec_number.trim() || !form.spec_title.trim()) {
      setToast({ type: 'error', text: 'Specification number and title are required.' });
      return;
    }

    setSaving(true);
    try {
      const payload = {
        spec_number: form.spec_number.trim(),
        spec_title: form.spec_title.trim(),
        spec_type: form.spec_type || '',
        current_alteration: form.current_alteration.trim(),
        controlling_agency: form.controlling_agency || null,
        source_reference: form.source_reference.trim(),
        is_active: form.is_active,
      };
      await (isEdit
        ? plMasterService.updateSpec(specNumber!, payload)
        : plMasterService.createSpec(payload));
      navigate('/pl-master');
    } catch {
      setToast({ type: 'error', text: 'Failed to save specification.' });
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return <div style={{ padding: 24, color: '#94a3b8' }}>Loading...</div>;
  }

  return (
    <div style={{ padding: 24 }}>
      <PageHeader title={isEdit ? `Edit ${form.spec_number}` : 'New Specification'} subtitle="Create or update a specification master record.">
        <Btn size="sm" variant="secondary" onClick={() => navigate('/pl-master')}>Cancel</Btn>
        <Btn size="sm" onClick={() => void handleSave()} loading={saving}>Save</Btn>
      </PageHeader>

      <Toast msg={toast} onClose={() => setToast(null)} />

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16 }}>
        <Field label="Spec Number" value={form.spec_number} onChange={value => setField('spec_number', value)} disabled={isEdit} />
        <Field label="Title" value={form.spec_title} onChange={value => setField('spec_title', value)} />
        <SelectField label="Spec Type" value={form.spec_type} onChange={value => setField('spec_type', value)} options={SPEC_TYPES} />
        <Field label="Alteration" value={form.current_alteration} onChange={value => setField('current_alteration', value)} />
        <SelectField label="Controlling Agency" value={form.controlling_agency} onChange={value => setField('controlling_agency', value)} options={agencies.map(agency => agency.agency_code)} />
        <Field label="Source Reference" value={form.source_reference} onChange={value => setField('source_reference', value)} full />
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
}: {
  label: string;
  value: string;
  onChange: (value: string) => void;
  disabled?: boolean;
  full?: boolean;
}) {
  return (
    <label style={{ display: 'grid', gap: 6, gridColumn: full ? '1 / -1' : undefined }}>
      <span style={{ color: '#94a3b8', fontSize: 12, fontWeight: 600 }}>{label}</span>
      <input
        value={value}
        disabled={disabled}
        onChange={event => onChange(event.target.value)}
        style={{ padding: '10px 12px', background: '#1e2332', border: '1px solid #2d3555', color: '#d1d5db', borderRadius: 8 }}
      />
    </label>
  );
}

function SelectField({
  label,
  value,
  onChange,
  options,
}: {
  label: string;
  value: string;
  onChange: (value: string) => void;
  options: string[];
}) {
  return (
    <label style={{ display: 'grid', gap: 6 }}>
      <span style={{ color: '#94a3b8', fontSize: 12, fontWeight: 600 }}>{label}</span>
      <select
        value={value}
        onChange={event => onChange(event.target.value)}
        style={{ padding: '10px 12px', background: '#1e2332', border: '1px solid #2d3555', color: '#d1d5db', borderRadius: 8 }}
      >
        <option value="">Select...</option>
        {options.map(option => (
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

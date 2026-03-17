import React, { useEffect, useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { Btn, PageHeader, Toast } from '../../components/common';
import type { ToastMsg } from '../../components/common';
import { plMasterService } from '../../services/plMasterService';

const DRAWING_TYPES = ['GA', 'AD', 'CD', 'SD', 'WD', 'PD', 'ID', 'FD', 'TD', 'JD', 'MD', 'RD', 'BD', 'LD'];
const READABILITY = ['READABLE', 'PARTIAL', 'POOR', 'ILLEGIBLE', 'MISSING', 'SUPERSEDED'];

export default function PLDrawingEditorPage() {
  const { drawingNumber } = useParams<{ drawingNumber?: string }>();
  const navigate = useNavigate();
  const isEdit = Boolean(drawingNumber);
  const [agencies, setAgencies] = useState<any[]>([]);
  const [loading, setLoading] = useState(isEdit);
  const [saving, setSaving] = useState(false);
  const [toast, setToast] = useState<ToastMsg | null>(null);
  const [form, setForm] = useState({
    drawing_number: '',
    drawing_title: '',
    drawing_type: '',
    current_alteration: '',
    controlling_agency: '',
    drawing_readable: 'READABLE',
    source_reference: '',
    is_active: true,
  });

  useEffect(() => {
    plMasterService.listAgencies().then(setAgencies).catch(() => {});
  }, []);

  useEffect(() => {
    if (!drawingNumber) return;
    plMasterService.getDrawing(drawingNumber)
      .then(data => {
        setForm({
          drawing_number: data.drawing_number ?? '',
          drawing_title: data.drawing_title ?? '',
          drawing_type: data.drawing_type ?? '',
          current_alteration: data.current_alteration ?? '',
          controlling_agency: data.controlling_agency ?? '',
          drawing_readable: data.drawing_readable ?? 'READABLE',
          source_reference: data.source_reference ?? '',
          is_active: Boolean(data.is_active),
        });
      })
      .catch(() => {
        setToast({ type: 'error', text: 'Failed to load drawing.' });
      })
      .finally(() => setLoading(false));
  }, [drawingNumber]);

  const setField = (key: string, value: string | boolean) => {
    setForm(current => ({ ...current, [key]: value }));
  };

  const handleSave = async () => {
    if (!form.drawing_number.trim() || !form.drawing_title.trim()) {
      setToast({ type: 'error', text: 'Drawing number and title are required.' });
      return;
    }

    setSaving(true);
    try {
      const payload = {
        drawing_number: form.drawing_number.trim(),
        drawing_title: form.drawing_title.trim(),
        drawing_type: form.drawing_type || '',
        current_alteration: form.current_alteration.trim(),
        controlling_agency: form.controlling_agency || null,
        drawing_readable: form.drawing_readable,
        source_reference: form.source_reference.trim(),
        is_active: form.is_active,
      };
      await (isEdit
        ? plMasterService.updateDrawing(drawingNumber!, payload)
        : plMasterService.createDrawing(payload));
      navigate('/pl-master');
    } catch {
      setToast({ type: 'error', text: 'Failed to save drawing.' });
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return <div style={{ padding: 24, color: '#94a3b8' }}>Loading...</div>;
  }

  return (
    <div style={{ padding: 24 }}>
      <PageHeader title={isEdit ? `Edit ${form.drawing_number}` : 'New Drawing'} subtitle="Create or update a drawing master record.">
        <Btn size="sm" variant="secondary" onClick={() => navigate('/pl-master')}>Cancel</Btn>
        <Btn size="sm" onClick={() => void handleSave()} loading={saving}>Save</Btn>
      </PageHeader>

      <Toast msg={toast} onClose={() => setToast(null)} />

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16 }}>
        <Field label="Drawing Number" value={form.drawing_number} onChange={value => setField('drawing_number', value)} disabled={isEdit} />
        <Field label="Title" value={form.drawing_title} onChange={value => setField('drawing_title', value)} />
        <SelectField label="Drawing Type" value={form.drawing_type} onChange={value => setField('drawing_type', value)} options={DRAWING_TYPES} />
        <Field label="Alteration" value={form.current_alteration} onChange={value => setField('current_alteration', value)} />
        <SelectField label="Controlling Agency" value={form.controlling_agency} onChange={value => setField('controlling_agency', value)} options={agencies.map(agency => agency.agency_code)} />
        <SelectField label="Readability" value={form.drawing_readable} onChange={value => setField('drawing_readable', value)} options={READABILITY} />
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

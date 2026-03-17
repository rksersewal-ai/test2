import React, { useCallback, useEffect, useState } from 'react';
import { Btn, ConfirmDialog, PageHeader, SearchBar, Toast } from '../components/common';
import type { ToastMsg } from '../components/common';
import { configService } from '../services/configService';
import type { ConfigStatus, ECN, LocoClass, LocoConfig } from '../types/config';
import './ConfigManagementPage.css';

type CTab = 'configs' | 'ecn';

const STATUS_CLS: Record<string, string> = {
  APPROVED: 'cfg-badge-approved',
  PENDING: 'cfg-badge-pending',
  SUPERSEDED: 'cfg-badge-superseded',
  REJECTED: 'cfg-badge-rejected',
};

const LOCO_TYPES = ['WAG-9', 'WAG-9H', 'WAG-9HH', 'WAP-7', 'WAP-5', 'WAG-12B', 'MEMU', 'DEMU'];

export default function ConfigManagementPage() {
  const [tab, setTab] = useState<CTab>('configs');

  return (
    <div className="cfg-page">
      <PageHeader title="Configuration Management" subtitle="Loco configurations, ECN register, and change control." />
      <div className="cfg-tabs">
        <button className={`cfg-tab${tab === 'configs' ? ' cfg-tab--active' : ''}`} onClick={() => setTab('configs')}>
          Loco Configs
        </button>
        <button className={`cfg-tab${tab === 'ecn' ? ' cfg-tab--active' : ''}`} onClick={() => setTab('ecn')}>
          ECN Register
        </button>
      </div>
      <div className="cfg-body">
        {tab === 'configs' ? <LocoConfigsTab /> : <ECNTab />}
      </div>
    </div>
  );
}

function LocoConfigsTab() {
  const [items, setItems] = useState<LocoConfig[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [search, setSearch] = useState('');
  const [loading, setLoading] = useState(false);
  const [toast, setToast] = useState<ToastMsg | null>(null);
  const [deleteTarget, setDeleteTarget] = useState<number | null>(null);
  const [showForm, setShowForm] = useState(false);
  const [editItem, setEditItem] = useState<LocoConfig | null>(null);
  const [locoFilter, setLocoFilter] = useState('');
  const [statusFilter, setStatusFilter] = useState('');
  const pageSize = 20;

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const params: Record<string, string> = { page: String(page), page_size: String(pageSize) };
      if (search.trim()) params.search = search.trim();
      if (locoFilter) params.loco_class = locoFilter;
      if (statusFilter) params.status = statusFilter;
      const data = await configService.listConfigs(params);
      setItems(data.results ?? data ?? []);
      setTotal(data.count ?? data.total_count ?? 0);
    } catch {
      setToast({ type: 'error', text: 'Failed to load configurations.' });
    } finally {
      setLoading(false);
    }
  }, [locoFilter, page, search, statusFilter]);

  useEffect(() => {
    void load();
  }, [load]);

  const handleDelete = async () => {
    if (!deleteTarget) return;
    try {
      await configService.deleteConfig(deleteTarget);
      setToast({ type: 'success', text: 'Configuration deleted.' });
      await load();
    } catch {
      setToast({ type: 'error', text: 'Delete failed.' });
    } finally {
      setDeleteTarget(null);
    }
  };

  const totalPages = Math.max(1, Math.ceil(total / pageSize));

  return (
    <div>
      <Toast msg={toast} onClose={() => setToast(null)} />
      <ConfirmDialog
        open={!!deleteTarget}
        title="Delete Config"
        message="Delete this loco configuration record? This cannot be undone."
        confirmLabel="Delete"
        onConfirm={handleDelete}
        onCancel={() => setDeleteTarget(null)}
      />

      {showForm && (
        <ConfigForm
          item={editItem}
          onClose={() => {
            setShowForm(false);
            setEditItem(null);
          }}
          onSuccess={message => {
            setShowForm(false);
            setEditItem(null);
            setToast({ type: 'success', text: message });
            void load();
          }}
        />
      )}

      <div className="cfg-toolbar">
        <SearchBar
          value={search}
          onChange={value => {
            setSearch(value);
            setPage(1);
          }}
          placeholder="Search serial no. or ECN ref..."
          width={260}
        />
        <select className="cfg-select" value={locoFilter} onChange={event => { setLocoFilter(event.target.value); setPage(1); }}>
          <option value="">All Loco Types</option>
          {LOCO_TYPES.map(type => <option key={type} value={type}>{type}</option>)}
        </select>
        <select className="cfg-select" value={statusFilter} onChange={event => { setStatusFilter(event.target.value); setPage(1); }}>
          <option value="">All Status</option>
          <option value="APPROVED">Approved</option>
          <option value="PENDING">Pending</option>
          <option value="SUPERSEDED">Superseded</option>
          <option value="REJECTED">Rejected</option>
        </select>
        <Btn size="sm" variant="ghost" onClick={() => void load()}>Refresh</Btn>
        <Btn size="sm" onClick={() => { setEditItem(null); setShowForm(true); }}>New Config</Btn>
      </div>

      <div className="cfg-table-wrap">
        <table className="cfg-table">
          <thead>
            <tr>
              <th>Loco Class</th>
              <th>Serial No.</th>
              <th>Config Ver.</th>
              <th>ECN Ref</th>
              <th>Effective Date</th>
              <th>Changed By</th>
              <th>Status</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {loading && (
              <tr><td colSpan={8} className="cfg-center cfg-muted">Loading...</td></tr>
            )}
            {!loading && items.length === 0 && (
              <tr><td colSpan={8} className="cfg-center cfg-muted">No configurations found.</td></tr>
            )}
            {items.map(item => (
              <tr key={item.id}>
                <td><span className="cfg-badge cfg-badge-blue">{item.loco_class}</span></td>
                <td className="cfg-mono">{item.serial_no}</td>
                <td className="cfg-mono cfg-purple">{item.config_version}</td>
                <td className="cfg-mono cfg-gold">{item.ecn_ref ?? '-'}</td>
                <td className="cfg-muted">{item.effective_date ?? '-'}</td>
                <td className="cfg-muted">{item.changed_by ?? '-'}</td>
                <td><span className={`cfg-badge ${STATUS_CLS[item.status] ?? ''}`}>{item.status}</span></td>
                <td className="cfg-actions">
                  <Btn size="sm" variant="ghost" onClick={() => { setEditItem(item); setShowForm(true); }}>Edit</Btn>
                  <Btn size="sm" variant="danger" onClick={() => setDeleteTarget(item.id)}>Delete</Btn>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div className="cfg-pagination">
        <span className="cfg-muted">{total} configs total</span>
        <div className="cfg-page-btns">
          <Btn size="sm" variant="secondary" disabled={page <= 1} onClick={() => setPage(current => current - 1)}>Prev</Btn>
          <span>Page {page} / {totalPages}</span>
          <Btn size="sm" variant="secondary" disabled={page >= totalPages} onClick={() => setPage(current => current + 1)}>Next</Btn>
        </div>
      </div>
    </div>
  );
}

function ECNTab() {
  const [items, setItems] = useState<ECN[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [search, setSearch] = useState('');
  const [loading, setLoading] = useState(false);
  const [toast, setToast] = useState<ToastMsg | null>(null);
  const [showForm, setShowForm] = useState(false);
  const [viewItem, setViewItem] = useState<ECN | null>(null);
  const pageSize = 20;

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const params: Record<string, string> = { page: String(page), page_size: String(pageSize) };
      if (search.trim()) params.search = search.trim();
      const data = await configService.listECN(params);
      setItems(data.results ?? data ?? []);
      setTotal(data.count ?? data.total_count ?? 0);
    } catch {
      setToast({ type: 'error', text: 'Failed to load ECN records.' });
    } finally {
      setLoading(false);
    }
  }, [page, search]);

  useEffect(() => {
    void load();
  }, [load]);

  const handleApprove = async (id: number) => {
    try {
      await configService.approveECN(id);
      setToast({ type: 'success', text: 'ECN approved.' });
      await load();
    } catch {
      setToast({ type: 'error', text: 'Approve failed.' });
    }
  };

  const totalPages = Math.max(1, Math.ceil(total / pageSize));

  return (
    <div>
      <Toast msg={toast} onClose={() => setToast(null)} />
      {showForm && (
        <ECNForm
          onClose={() => setShowForm(false)}
          onSuccess={message => {
            setShowForm(false);
            setToast({ type: 'success', text: message });
            void load();
          }}
        />
      )}
      {viewItem && <ECNViewModal item={viewItem} onClose={() => setViewItem(null)} />}

      <div className="cfg-toolbar">
        <SearchBar
          value={search}
          onChange={value => {
            setSearch(value);
            setPage(1);
          }}
          placeholder="Search ECN number or subject..."
          width={300}
        />
        <Btn size="sm" variant="ghost" onClick={() => void load()}>Refresh</Btn>
        <Btn size="sm" onClick={() => setShowForm(true)}>New ECN</Btn>
      </div>

      <div className="cfg-table-wrap">
        <table className="cfg-table">
          <thead>
            <tr>
              <th>ECN Number</th>
              <th>Subject</th>
              <th>Loco Class</th>
              <th>Raised By</th>
              <th>Date</th>
              <th>Status</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {loading && (
              <tr><td colSpan={7} className="cfg-center cfg-muted">Loading...</td></tr>
            )}
            {!loading && items.length === 0 && (
              <tr><td colSpan={7} className="cfg-center cfg-muted">No ECN records found.</td></tr>
            )}
            {items.map(item => (
              <tr key={item.id}>
                <td className="cfg-mono cfg-gold">{item.ecn_number ?? '-'}</td>
                <td className="cfg-desc">{item.subject ?? '-'}</td>
                <td><span className="cfg-badge cfg-badge-blue">{item.loco_class ?? '-'}</span></td>
                <td className="cfg-muted">{item.raised_by_name ?? item.raised_by ?? '-'}</td>
                <td className="cfg-muted">{item.date ?? '-'}</td>
                <td><span className={`cfg-badge ${STATUS_CLS[item.status] ?? ''}`}>{item.status}</span></td>
                <td className="cfg-actions">
                  {item.status === 'PENDING' && (
                    <Btn size="sm" variant="primary" onClick={() => void handleApprove(item.id)}>Approve</Btn>
                  )}
                  <Btn size="sm" variant="ghost" onClick={() => setViewItem(item)}>View</Btn>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div className="cfg-pagination">
        <span className="cfg-muted">{total} ECN records</span>
        <div className="cfg-page-btns">
          <Btn size="sm" variant="secondary" disabled={page <= 1} onClick={() => setPage(current => current - 1)}>Prev</Btn>
          <span>Page {page} / {totalPages}</span>
          <Btn size="sm" variant="secondary" disabled={page >= totalPages} onClick={() => setPage(current => current + 1)}>Next</Btn>
        </div>
      </div>
    </div>
  );
}

function ConfigForm({
  item,
  onClose,
  onSuccess,
}: {
  item: LocoConfig | null;
  onClose: () => void;
  onSuccess: (message: string) => void;
}) {
  const isEdit = Boolean(item);
  const [form, setForm] = useState({
    loco_class: (item?.loco_class ?? '') as '' | LocoClass,
    serial_no: item?.serial_no ?? '',
    config_version: item?.config_version ?? '',
    ecn_ref: item?.ecn_ref ?? '',
    effective_date: item?.effective_date ?? '',
    changed_by: item?.changed_by ?? '',
    status: (item?.status ?? 'PENDING') as ConfigStatus,
    remarks: item?.remarks ?? '',
  });
  const [saving, setSaving] = useState(false);
  const [errors, setErrors] = useState<Record<string, string>>({});

  const setField = (key: string, value: string) => {
    setForm(current => ({ ...current, [key]: value }));
    setErrors(current => ({ ...current, [key]: '' }));
  };

  const validate = () => {
    const nextErrors: Record<string, string> = {};
    if (!form.loco_class) nextErrors.loco_class = 'Required';
    if (!form.serial_no.trim()) nextErrors.serial_no = 'Required';
    if (!form.config_version.trim()) nextErrors.config_version = 'Required';
    setErrors(nextErrors);
    return Object.keys(nextErrors).length === 0;
  };

  const handleSave = async () => {
    if (!validate()) return;
    setSaving(true);
    try {
      const payload: Partial<LocoConfig> = {
        serial_no: form.serial_no,
        config_version: form.config_version,
        ecn_ref: form.ecn_ref,
        effective_date: form.effective_date || null,
        changed_by: form.changed_by,
        status: form.status,
        remarks: form.remarks,
        ...(form.loco_class ? { loco_class: form.loco_class } : {}),
      };
      if (item) {
        await configService.updateConfig(item.id, payload);
      } else {
        await configService.createConfig(payload);
      }
      onSuccess(isEdit ? 'Configuration updated.' : 'Configuration created.');
    } catch (err: any) {
      setErrors({ _global: JSON.stringify(err?.response?.data ?? 'Save failed.') });
    } finally {
      setSaving(false);
    }
  };

  return (
    <ModalShell title={isEdit ? 'Edit Config' : 'New Loco Config'} onClose={onClose}>
      {errors._global && <div className="cfg-alert-err">{errors._global}</div>}
      <div className="cfg-form-grid">
        <FormField label="Loco Class" error={errors.loco_class}>
          <select value={form.loco_class} onChange={event => setField('loco_class', event.target.value)}>
            <option value="">Select...</option>
            {LOCO_TYPES.map(type => <option key={type} value={type}>{type}</option>)}
          </select>
        </FormField>
        <FormField label="Serial No." error={errors.serial_no}>
          <input value={form.serial_no} onChange={event => setField('serial_no', event.target.value)} />
        </FormField>
        <FormField label="Config Version" error={errors.config_version}>
          <input value={form.config_version} onChange={event => setField('config_version', event.target.value)} />
        </FormField>
        <FormField label="ECN Reference">
          <input value={form.ecn_ref} onChange={event => setField('ecn_ref', event.target.value)} />
        </FormField>
        <FormField label="Effective Date">
          <input type="date" value={form.effective_date} onChange={event => setField('effective_date', event.target.value)} />
        </FormField>
        <FormField label="Changed By">
          <input value={form.changed_by} onChange={event => setField('changed_by', event.target.value)} />
        </FormField>
        <FormField label="Status">
          <select value={form.status} onChange={event => setField('status', event.target.value)}>
            <option value="PENDING">Pending</option>
            <option value="APPROVED">Approved</option>
            <option value="SUPERSEDED">Superseded</option>
            <option value="REJECTED">Rejected</option>
          </select>
        </FormField>
        <FormField label="Remarks" full>
          <input value={form.remarks} onChange={event => setField('remarks', event.target.value)} />
        </FormField>
      </div>
      <div className="cfg-modal-footer">
        <Btn variant="secondary" onClick={onClose} disabled={saving}>Cancel</Btn>
        <Btn variant="primary" onClick={handleSave} loading={saving}>{isEdit ? 'Save Changes' : 'Create Config'}</Btn>
      </div>
    </ModalShell>
  );
}

function ECNForm({
  onClose,
  onSuccess,
}: {
  onClose: () => void;
  onSuccess: (message: string) => void;
}) {
  const [form, setForm] = useState({
    ecn_number: '',
    subject: '',
    loco_class: '' as '' | LocoClass,
    description: '',
    status: 'PENDING' as ConfigStatus,
    date: '',
    remarks: '',
  });
  const [saving, setSaving] = useState(false);
  const [errors, setErrors] = useState<Record<string, string>>({});

  const setField = (key: string, value: string) => {
    setForm(current => ({ ...current, [key]: value }));
    setErrors(current => ({ ...current, [key]: '' }));
  };

  const validate = () => {
    const nextErrors: Record<string, string> = {};
    if (!form.ecn_number.trim()) nextErrors.ecn_number = 'Required';
    if (!form.subject.trim()) nextErrors.subject = 'Required';
    setErrors(nextErrors);
    return Object.keys(nextErrors).length === 0;
  };

  const handleSave = async () => {
    if (!validate()) return;
    setSaving(true);
    try {
      const payload: Partial<ECN> = {
        ecn_number: form.ecn_number,
        subject: form.subject,
        description: form.description,
        status: form.status,
        date: form.date || null,
        remarks: form.remarks,
        ...(form.loco_class ? { loco_class: form.loco_class } : {}),
      };
      await configService.createECN(payload);
      onSuccess('ECN created.');
    } catch (err: any) {
      setErrors({ _global: JSON.stringify(err?.response?.data ?? 'Save failed.') });
    } finally {
      setSaving(false);
    }
  };

  return (
    <ModalShell title="New ECN" onClose={onClose}>
      {errors._global && <div className="cfg-alert-err">{errors._global}</div>}
      <div className="cfg-form-grid">
        <FormField label="ECN Number" error={errors.ecn_number}>
          <input value={form.ecn_number} onChange={event => setField('ecn_number', event.target.value)} />
        </FormField>
        <FormField label="Date">
          <input type="date" value={form.date} onChange={event => setField('date', event.target.value)} />
        </FormField>
        <FormField label="Subject" error={errors.subject} full>
          <input value={form.subject} onChange={event => setField('subject', event.target.value)} />
        </FormField>
        <FormField label="Loco Class">
          <select value={form.loco_class} onChange={event => setField('loco_class', event.target.value)}>
            <option value="">Select...</option>
            {LOCO_TYPES.map(type => <option key={type} value={type}>{type}</option>)}
          </select>
        </FormField>
        <FormField label="Status">
          <select value={form.status} onChange={event => setField('status', event.target.value)}>
            <option value="PENDING">Pending</option>
            <option value="APPROVED">Approved</option>
            <option value="SUPERSEDED">Superseded</option>
            <option value="REJECTED">Rejected</option>
          </select>
        </FormField>
        <FormField label="Description" full>
          <textarea rows={4} value={form.description} onChange={event => setField('description', event.target.value)} />
        </FormField>
        <FormField label="Remarks" full>
          <input value={form.remarks} onChange={event => setField('remarks', event.target.value)} />
        </FormField>
      </div>
      <div className="cfg-modal-footer">
        <Btn variant="secondary" onClick={onClose} disabled={saving}>Cancel</Btn>
        <Btn variant="primary" onClick={handleSave} loading={saving}>Create ECN</Btn>
      </div>
    </ModalShell>
  );
}

function ECNViewModal({
  item,
  onClose,
}: {
  item: ECN;
  onClose: () => void;
}) {
  const rows = [
    ['ECN Number', item.ecn_number ?? '-'],
    ['Subject', item.subject ?? '-'],
    ['Loco Class', item.loco_class ?? '-'],
    ['Status', item.status ?? '-'],
    ['Date', item.date ?? '-'],
    ['Raised By', item.raised_by_name ?? item.raised_by ?? '-'],
    ['Approved By', item.approved_by_name ?? '-'],
    ['Approved At', item.approved_at ?? '-'],
    ['Description', item.description ?? '-'],
    ['Remarks', item.remarks ?? '-'],
  ];

  return (
    <ModalShell title="ECN Details" onClose={onClose}>
      <div className="cfg-form-grid">
        {rows.map(([label, value]) => (
          <div key={label} className="cfg-field" style={{ gridColumn: '1 / -1' }}>
            <label>{label}</label>
            <div className="cfg-readonly">{value}</div>
          </div>
        ))}
      </div>
      <div className="cfg-modal-footer">
        <Btn variant="primary" onClick={onClose}>Close</Btn>
      </div>
    </ModalShell>
  );
}

function ModalShell({
  title,
  onClose,
  children,
}: {
  title: string;
  onClose: () => void;
  children: React.ReactNode;
}) {
  return (
    <div className="cfg-modal-overlay" onClick={onClose}>
      <div className="cfg-modal" onClick={event => event.stopPropagation()}>
        <div className="cfg-modal-header">
          <span>{title}</span>
          <button className="cfg-modal-close" onClick={onClose}>×</button>
        </div>
        <div className="cfg-modal-body">{children}</div>
      </div>
    </div>
  );
}

function FormField({
  label,
  error,
  full,
  children,
}: {
  label: string;
  error?: string;
  full?: boolean;
  children: React.ReactNode;
}) {
  return (
    <div className="cfg-field" style={{ gridColumn: full ? '1 / -1' : undefined }}>
      <label>{label}</label>
      {children}
      {error && <span className="cfg-err">{error}</span>}
    </div>
  );
}

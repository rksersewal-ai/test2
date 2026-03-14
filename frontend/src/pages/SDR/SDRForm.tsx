// =============================================================================
// FILE: frontend/src/pages/SDR/SDRForm.tsx
//
// Shared create + edit form.
// Props:
//   mode = 'create' | 'edit'
//   initialData (edit only) — pre-filled values
//   onSave   — called after successful save
//   onCancel — called when Cancel is clicked
// =============================================================================
import React, { useState, useCallback, useRef } from 'react';
import type {
  SDRRecordForm, SDRItem, DocSearchResult, DrawingSize, DocType
} from '../../types/sdr';
import { DRAWING_SIZES, EMPTY_ITEM, EMPTY_FORM } from '../../types/sdr';
import { sdrService } from '../../services/sdrService';

interface Props {
  mode: 'create' | 'edit';
  initialData?: SDRRecordForm;
  recordId?: number;
  sdrNumber?: string;
  onSave:   () => void;
  onCancel: () => void;
}

export default function SDRForm({
  mode, initialData, recordId, sdrNumber, onSave, onCancel
}: Props) {
  const [form, setForm]         = useState<SDRRecordForm>(initialData ?? { ...EMPTY_FORM });
  const [saving, setSaving]     = useState(false);
  const [errors, setErrors]     = useState<Record<string, string>>({});
  const [toast,  setToast]      = useState('');

  // Per-item doc search state
  const [searchQuery, setSearchQuery]   = useState<Record<number, string>>({});
  const [searchResults, setSearchResults] = useState<Record<number, DocSearchResult[]>>({});
  const [searchLoading, setSearchLoading] = useState<Record<number, boolean>>({});
  const searchTimers = useRef<Record<number, ReturnType<typeof setTimeout>>>({});

  // ── Header field change ──────────────────────────────────────────────────
  const setHeader = (field: keyof SDRRecordForm, value: string) => {
    setForm(f => ({ ...f, [field]: value }));
    setErrors(e => ({ ...e, [field]: '' }));
  };

  // ── Item helpers ─────────────────────────────────────────────────────────
  const updateItem = (idx: number, patch: Partial<SDRItem>) => {
    setForm(f => {
      const items = [...f.items];
      items[idx]  = { ...items[idx], ...patch };
      return { ...f, items };
    });
  };

  const addItem = () => {
    setForm(f => ({ ...f, items: [...f.items, { ...EMPTY_ITEM }] }));
  };

  const removeItem = (idx: number) => {
    setForm(f => ({ ...f, items: f.items.filter((_, i) => i !== idx) }));
    setSearchQuery(q  => { const n = { ...q };  delete n[idx]; return n; });
    setSearchResults(r => { const n = { ...r }; delete n[idx]; return n; });
  };

  // ── Doc search typeahead ─────────────────────────────────────────────────
  const handleDocSearch = useCallback((idx: number, q: string, type: DocType) => {
    setSearchQuery(prev => ({ ...prev, [idx]: q }));
    clearTimeout(searchTimers.current[idx]);
    if (q.length < 2) {
      setSearchResults(prev => ({ ...prev, [idx]: [] }));
      return;
    }
    searchTimers.current[idx] = setTimeout(async () => {
      setSearchLoading(prev => ({ ...prev, [idx]: true }));
      try {
        const results = await sdrService.search(q, type);
        setSearchResults(prev => ({ ...prev, [idx]: results }));
      } finally {
        setSearchLoading(prev => ({ ...prev, [idx]: false }));
      }
    }, 300);
  }, []);

  const selectDoc = (idx: number, doc: DocSearchResult) => {
    updateItem(idx, {
      document_type:   doc.type,
      drawing:         doc.type === 'DRAWING' ? doc.id : null,
      specification:   doc.type === 'SPEC'    ? doc.id : null,
      document_number: doc.number,
      document_title:  doc.title,
      alteration_no:   doc.current_alteration,
    });
    setSearchQuery(q  => ({ ...q,   [idx]: doc.number }));
    setSearchResults(r => ({ ...r,  [idx]: [] }));
  };

  // ── Validation ───────────────────────────────────────────────────────────
  const validate = (): boolean => {
    const e: Record<string, string> = {};
    if (!form.issue_date)          e.issue_date          = 'Required';
    if (!form.shop_name.trim())    e.shop_name           = 'Required';
    if (!form.requesting_official.trim()) e.requesting_official = 'Required';
    if (!form.issuing_official.trim())    e.issuing_official    = 'Required';
    if (!form.receiving_official.trim())  e.receiving_official  = 'Required';
    if (form.items.length === 0)   e.items = 'Add at least one drawing/specification.';
    form.items.forEach((item, i) => {
      if (!item.document_number)
        e[`item_${i}_doc`] = 'Select a document.';
      if (!item.copies || item.copies < 1)
        e[`item_${i}_copies`] = 'Min 1.';
    });
    setErrors(e);
    return Object.keys(e).length === 0;
  };

  // ── Save ─────────────────────────────────────────────────────────────────
  const handleSave = async () => {
    if (!validate()) return;
    setSaving(true);
    try {
      if (mode === 'create') {
        await sdrService.create(form);
        setToast('Record saved successfully.');
      } else if (recordId) {
        await sdrService.update(recordId, form);
        setToast('Record updated successfully.');
      }
      setTimeout(() => onSave(), 700);
    } catch (err: any) {
      const msg = err?.response?.data
        ? JSON.stringify(err.response.data)
        : 'Save failed. Please try again.';
      setErrors({ _global: msg });
    } finally {
      setSaving(false);
    }
  };

  // ── Render ────────────────────────────────────────────────────────────────
  return (
    <div className="sdr-form">
      {/* ── Title ── */}
      <div className="form-title">
        {mode === 'create'
          ? 'New Issue Record'
          : `Edit — ${sdrNumber}`}
      </div>

      {toast && <div className="alert alert-success">{toast}</div>}
      {errors._global && <div className="alert alert-error">{errors._global}</div>}

      {/* ── Header Section ── */}
      <section className="form-section">
        <h3>Issue Details</h3>
        <div className="form-grid-2">
          <div className="form-field">
            <label>Issue Date <span className="req">*</span></label>
            <input type="date" value={form.issue_date}
              onChange={e => setHeader('issue_date', e.target.value)} />
            {errors.issue_date && <span className="field-error">{errors.issue_date}</span>}
          </div>

          <div className="form-field">
            <label>Shop Name <span className="req">*</span></label>
            <input type="text" placeholder="e.g. AC Machine Shop"
              value={form.shop_name}
              onChange={e => setHeader('shop_name', e.target.value)} />
            {errors.shop_name && <span className="field-error">{errors.shop_name}</span>}
          </div>

          <div className="form-field">
            <label>Requesting Official <span className="req">*</span></label>
            <input type="text" placeholder="Name of official requesting prints"
              value={form.requesting_official}
              onChange={e => setHeader('requesting_official', e.target.value)} />
            {errors.requesting_official && <span className="field-error">{errors.requesting_official}</span>}
          </div>

          <div className="form-field">
            <label>Issuing Official <span className="req">*</span></label>
            <input type="text" placeholder="LDO staff issuing the prints"
              value={form.issuing_official}
              onChange={e => setHeader('issuing_official', e.target.value)} />
            {errors.issuing_official && <span className="field-error">{errors.issuing_official}</span>}
          </div>

          <div className="form-field">
            <label>Receiving Official <span className="req">*</span></label>
            <input type="text" placeholder="Person who physically received"
              value={form.receiving_official}
              onChange={e => setHeader('receiving_official', e.target.value)} />
            {errors.receiving_official && <span className="field-error">{errors.receiving_official}</span>}
          </div>

          <div className="form-field">
            <label>Remarks</label>
            <textarea rows={2} value={form.remarks}
              onChange={e => setHeader('remarks', e.target.value)} />
          </div>
        </div>
      </section>

      {/* ── Items Section ── */}
      <section className="form-section">
        <div className="section-header">
          <h3>Drawings / Specifications</h3>
          <button type="button" className="btn btn-sm btn-secondary" onClick={addItem}>
            + Add Row
          </button>
        </div>
        {errors.items && <div className="field-error mb-8">{errors.items}</div>}

        <table className="items-table">
          <thead>
            <tr>
              <th style={{width:36}}>#</th>
              <th style={{width:100}}>Type</th>
              <th>Document (search &amp; select)</th>
              <th style={{width:80}}>Alt. No.</th>
              <th style={{width:80}}>Size</th>
              <th style={{width:80}}>Copies</th>
              <th style={{width:110}}>Controlled Copy?</th>
              <th style={{width:40}}></th>
            </tr>
          </thead>
          <tbody>
            {form.items.map((item, idx) => (
              <tr key={idx}>
                {/* # */}
                <td className="center muted">{idx + 1}</td>

                {/* Type */}
                <td>
                  <select
                    value={item.document_type}
                    onChange={e => {
                      updateItem(idx, {
                        document_type:   e.target.value as DocType,
                        drawing:         null,
                        specification:   null,
                        document_number: '',
                        document_title:  '',
                        alteration_no:   '',
                      });
                      setSearchQuery(q  => ({ ...q,  [idx]: '' }));
                      setSearchResults(r => ({ ...r, [idx]: [] }));
                    }}
                  >
                    <option value="DRAWING">Drawing</option>
                    <option value="SPEC">Spec</option>
                  </select>
                </td>

                {/* Document search */}
                <td className="doc-search-cell">
                  <div className="doc-search-wrapper">
                    <input
                      type="text"
                      placeholder={`Search ${item.document_type === 'DRAWING' ? 'drawing' : 'spec'} number…`}
                      value={searchQuery[idx] ?? item.document_number}
                      onChange={e =>
                        handleDocSearch(idx, e.target.value, item.document_type)
                      }
                    />
                    {searchLoading[idx] && <span className="search-spinner">…</span>}
                    {(searchResults[idx]?.length ?? 0) > 0 && (
                      <ul className="search-dropdown">
                        {searchResults[idx].map(doc => (
                          <li key={doc.id} onClick={() => selectDoc(idx, doc)}>
                            <strong>{doc.number}</strong>
                            {doc.title && <span> — {doc.title}</span>}
                            {doc.current_alteration &&
                              <span className="alt-tag"> Alt.{doc.current_alteration}</span>}
                          </li>
                        ))}
                      </ul>
                    )}
                  </div>
                  {item.document_title && (
                    <div className="doc-subtitle">{item.document_title}</div>
                  )}
                  {errors[`item_${idx}_doc`] && (
                    <span className="field-error">{errors[`item_${idx}_doc`]}</span>
                  )}
                </td>

                {/* Alt no (read-only, auto-filled) */}
                <td>
                  <input type="text" value={item.alteration_no} readOnly
                    className="readonly" tabIndex={-1} />
                </td>

                {/* Size */}
                <td>
                  <select
                    value={item.size}
                    onChange={e => updateItem(idx, { size: e.target.value as DrawingSize })}
                  >
                    {DRAWING_SIZES.map(s => (
                      <option key={s} value={s}>{s}</option>
                    ))}
                  </select>
                </td>

                {/* Copies */}
                <td>
                  <input
                    type="number" min={1} max={99}
                    value={item.copies}
                    onChange={e => updateItem(idx, { copies: parseInt(e.target.value) || 1 })}
                  />
                  {errors[`item_${idx}_copies`] && (
                    <span className="field-error">{errors[`item_${idx}_copies`]}</span>
                  )}
                </td>

                {/* Controlled copy */}
                <td className="center">
                  <label className="checkbox-label">
                    <input
                      type="checkbox"
                      checked={item.controlled_copy}
                      onChange={e => updateItem(idx, { controlled_copy: e.target.checked })}
                    />
                    <span>{item.controlled_copy ? 'Yes' : 'No'}</span>
                  </label>
                </td>

                {/* Remove row */}
                <td className="center">
                  <button
                    type="button"
                    className="btn btn-icon btn-danger"
                    onClick={() => removeItem(idx)}
                    title="Remove row"
                    disabled={form.items.length === 1}
                  >
                    ✕
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </section>

      {/* ── Action Buttons ── */}
      <div className="form-actions">
        <button
          type="button"
          className="btn btn-secondary"
          onClick={onCancel}
          disabled={saving}
        >
          Cancel
        </button>
        <button
          type="button"
          className="btn btn-primary"
          onClick={handleSave}
          disabled={saving}
        >
          {saving
            ? 'Saving…'
            : mode === 'create' ? '💾 Save Record' : '💾 Save Changes'}
        </button>
      </div>
    </div>
  );
}

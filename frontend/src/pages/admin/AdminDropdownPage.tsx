// =============================================================================
// FILE: frontend/src/pages/admin/AdminDropdownPage.tsx
// PURPOSE: Admin page to manage all dropdown groups (add, edit label, delete/deactivate)
// =============================================================================
import React, { useEffect, useState } from 'react';
import { dropdownApi } from '../../services/dropdownApi';
import type { DropdownItem, DropdownGroupKey } from '../../types/dropdown';
import { DROPDOWN_GROUPS, DROPDOWN_GROUP_LABELS } from '../../types/dropdown';

const GROUP_KEYS = Object.values(DROPDOWN_GROUPS) as DropdownGroupKey[];

export const AdminDropdownPage: React.FC = () => {
  const [activeGroup, setActiveGroup] = useState<DropdownGroupKey>(DROPDOWN_GROUPS.SECTION);
  const [items, setItems] = useState<DropdownItem[]>([]);
  const [loading, setLoading] = useState(false);
  const [newCode, setNewCode] = useState('');
  const [newLabel, setNewLabel] = useState('');
  const [newSortOverride, setNewSortOverride] = useState('');
  const [editId, setEditId] = useState<number | null>(null);
  const [editLabel, setEditLabel] = useState('');
  const [editSort, setEditSort] = useState('');
  const [msg, setMsg] = useState('');
  const [err, setErr] = useState('');

  const loadItems = async () => {
    setLoading(true);
    try {
      const data = await dropdownApi.adminListGroup(activeGroup);
      // Sort alphabetically by label (admin view shows all including inactive)
      setItems([...data].sort((a, b) => a.label.localeCompare(b.label)));
    } catch (e: any) {
      setErr(e.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    setMsg(''); setErr('');
    loadItems();
  }, [activeGroup]); // eslint-disable-line

  const handleAdd = async () => {
    if (!newCode.trim() || !newLabel.trim()) {
      setErr('Code and Label are required.');
      return;
    }
    try {
      await dropdownApi.adminCreate(activeGroup, {
        code: newCode.trim().toUpperCase(),
        label: newLabel.trim(),
        sort_override: newSortOverride ? Number(newSortOverride) : null,
      });
      setMsg('Item added.');
      setNewCode(''); setNewLabel(''); setNewSortOverride('');
      loadItems();
    } catch (e: any) { setErr(e.message); }
  };

  const handleEdit = async (item: DropdownItem) => {
    setEditId(item.id);
    setEditLabel(item.label);
    setEditSort(item.sort_override?.toString() ?? '');
  };

  const handleSaveEdit = async (itemId: number) => {
    try {
      await dropdownApi.adminUpdate(activeGroup, itemId, {
        label: editLabel.trim(),
        sort_override: editSort ? Number(editSort) : null,
      });
      setMsg('Item updated.');
      setEditId(null);
      loadItems();
    } catch (e: any) { setErr(e.message); }
  };

  const handleDeactivate = async (item: DropdownItem) => {
    if (item.is_system) { setErr('System items cannot be deactivated.'); return; }
    if (!window.confirm(`Deactivate "${item.label}"? It will no longer appear in dropdowns.`)) return;
    try {
      await dropdownApi.adminDeactivate(activeGroup, item.id);
      setMsg('Item deactivated.');
      loadItems();
    } catch (e: any) { setErr(e.message); }
  };

  const handleDelete = async (item: DropdownItem) => {
    if (item.is_system) { setErr('System items cannot be deleted.'); return; }
    if (!window.confirm(`Permanently delete "${item.label}"? This cannot be undone.`)) return;
    try {
      await dropdownApi.adminDelete(activeGroup, item.id);
      setMsg('Item deleted.');
      loadItems();
    } catch (e: any) { setErr(e.message); }
  };

  return (
    <div className="admin-dropdown-page">
      <h2>Dropdown Management</h2>
      <p className="admin-dropdown-page__hint">
        Manage dropdown options used across the Work Ledger form.
        Items marked <strong>System</strong> can have their label edited but cannot be deleted or deactivated.
        All dropdowns are sorted alphabetically by default.
      </p>

      {/* Group selector */}
      <div className="admin-dropdown-page__groups">
        {GROUP_KEYS.map((gk) => (
          <button
            key={gk}
            className={`admin-dd-tab ${activeGroup === gk ? 'admin-dd-tab--active' : ''}`}
            onClick={() => setActiveGroup(gk)}
          >
            {DROPDOWN_GROUP_LABELS[gk]}
          </button>
        ))}
      </div>

      {msg && <div className="wl-alert wl-alert--success">{msg}</div>}
      {err && <div className="wl-alert wl-alert--error">{err}</div>}

      {/* Add new item form */}
      <div className="admin-dd-add">
        <h3>Add New Item to: {DROPDOWN_GROUP_LABELS[activeGroup]}</h3>
        <div className="admin-dd-add__row">
          <input
            placeholder="CODE (e.g. NEW_ITEM)"
            value={newCode}
            onChange={(e) => setNewCode(e.target.value.toUpperCase())}
            className="admin-dd-input"
          />
          <input
            placeholder="Label (display text)"
            value={newLabel}
            onChange={(e) => setNewLabel(e.target.value)}
            className="admin-dd-input admin-dd-input--wide"
          />
          <input
            type="number"
            placeholder="Sort override (optional)"
            value={newSortOverride}
            onChange={(e) => setNewSortOverride(e.target.value)}
            className="admin-dd-input admin-dd-input--narrow"
          />
          <button className="wl-btn wl-btn--primary" onClick={handleAdd}>Add Item</button>
        </div>
      </div>

      {/* Item table */}
      {loading ? (
        <p className="wl-loading">Loading items...</p>
      ) : (
        <table className="wl-table admin-dd-table">
          <thead>
            <tr>
              <th>Code</th>
              <th>Label</th>
              <th>Sort Override</th>
              <th>Active</th>
              <th>System</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {items.length === 0 && (
              <tr><td colSpan={6} className="wl-empty">No items found.</td></tr>
            )}
            {items.map((item) => (
              <tr key={item.id} className={item.is_active === false ? 'admin-dd-row--inactive' : ''}>
                <td><code>{item.code}</code></td>
                <td>
                  {editId === item.id ? (
                    <input
                      value={editLabel}
                      onChange={(e) => setEditLabel(e.target.value)}
                      className="admin-dd-input"
                    />
                  ) : item.label}
                </td>
                <td>
                  {editId === item.id ? (
                    <input
                      type="number"
                      value={editSort}
                      onChange={(e) => setEditSort(e.target.value)}
                      className="admin-dd-input admin-dd-input--narrow"
                    />
                  ) : (item.sort_override ?? <span className="wl-muted">alpha</span>)}
                </td>
                <td>{item.is_active !== false ? '✅' : '❌'}</td>
                <td>{item.is_system ? <span className="wl-badge wl-badge--system">System</span> : '-'}</td>
                <td className="admin-dd-actions">
                  {editId === item.id ? (
                    <>
                      <button className="wl-btn wl-btn--sm wl-btn--primary" onClick={() => handleSaveEdit(item.id)}>Save</button>
                      <button className="wl-btn wl-btn--sm" onClick={() => setEditId(null)}>Cancel</button>
                    </>
                  ) : (
                    <>
                      <button className="wl-btn wl-btn--sm" onClick={() => handleEdit(item)}>Edit</button>
                      {!item.is_system && item.is_active !== false && (
                        <button className="wl-btn wl-btn--sm wl-btn--warn" onClick={() => handleDeactivate(item)}>Deactivate</button>
                      )}
                      {!item.is_system && (
                        <button className="wl-btn wl-btn--sm wl-btn--danger" onClick={() => handleDelete(item)}>Delete</button>
                      )}
                    </>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
};

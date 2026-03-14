// =============================================================================
// FILE: frontend/src/pages/SDR/SDRList.tsx
// List of all SDR records with search and navigation to create/edit.
// =============================================================================
import React, { useEffect, useState, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { sdrService } from '../../services/sdrService';
import type { SDRRecord } from '../../types/sdr';

export default function SDRList() {
  const navigate = useNavigate();
  const [records, setRecords]   = useState<SDRRecord[]>([]);
  const [loading, setLoading]   = useState(true);
  const [search,  setSearch]    = useState('');
  const [error,   setError]     = useState('');

  const load = useCallback(async () => {
    setLoading(true);
    setError('');
    try {
      const params = search ? { search } : undefined;
      const data   = await sdrService.list(params);
      setRecords(data);
    } catch {
      setError('Failed to load SDR records.');
    } finally {
      setLoading(false);
    }
  }, [search]);

  useEffect(() => { load(); }, [load]);

  const handleDelete = async (id: number, sdrNumber: string) => {
    if (!window.confirm(`Delete SDR record ${sdrNumber}?`)) return;
    await sdrService.delete(id);
    load();
  };

  return (
    <div className="sdr-list-page">
      {/* ── Header ── */}
      <div className="page-header">
        <div>
          <h2>Shop Drawing Issue Register</h2>
          <p className="subtitle">Record of drawings / specifications issued to shops</p>
        </div>
        <button className="btn btn-primary" onClick={() => navigate('/sdr/new')}>
          + New Issue Record
        </button>
      </div>

      {/* ── Search ── */}
      <div className="search-bar">
        <input
          type="text"
          placeholder="Search by SDR No., shop, official, drawing number…"
          value={search}
          onChange={e => setSearch(e.target.value)}
        />
      </div>

      {/* ── Table ── */}
      {error && <div className="alert alert-error">{error}</div>}
      {loading ? (
        <div className="loading">Loading…</div>
      ) : (
        <table className="data-table">
          <thead>
            <tr>
              <th>SDR No.</th>
              <th>Issue Date</th>
              <th>Shop</th>
              <th>Requesting Official</th>
              <th>Issuing Official</th>
              <th>Receiving Official</th>
              <th>Items</th>
              <th>Controlled?</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {records.length === 0 && (
              <tr><td colSpan={9} className="empty">No records found.</td></tr>
            )}
            {records.map(rec => (
              <tr key={rec.id}>
                <td><strong>{rec.sdr_number}</strong></td>
                <td>{rec.issue_date}</td>
                <td>{rec.shop_name}</td>
                <td>{rec.requesting_official}</td>
                <td>{rec.issuing_official}</td>
                <td>{rec.receiving_official}</td>
                <td className="center">{rec.total_items}</td>
                <td className="center">
                  {rec.has_controlled_copy
                    ? <span className="badge badge-navy">YES</span>
                    : <span className="muted">—</span>}
                </td>
                <td className="actions">
                  <button
                    className="btn btn-sm btn-secondary"
                    onClick={() => navigate(`/sdr/${rec.id}/edit`)}
                    title="Edit this record"
                  >
                    ✏️ Edit
                  </button>
                  <button
                    className="btn btn-sm btn-danger"
                    onClick={() => handleDelete(rec.id, rec.sdr_number)}
                    title="Delete this record"
                  >
                    🗑
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}

// =============================================================================
// FILE: frontend/src/pages/DashboardPage.tsx
// BUG FIX 1: Quick-link cards ("+ Upload Document", "New SDR", "OCR Queue")
//            called window.location.href which caused full page reload and lost
//            React state. Now uses useNavigate() for SPA navigation.
// BUG FIX 2: dashboard.ts service imported from services/dashboard.ts which
//            only had 1 method (getDashboard) but page destructured
//            {stats, recent_docs, pending_approvals} — correct destructure added.
// BUG FIX 3: "Pending Approvals" section rendered pending_approvals.map() but
//            on API error state was undefined — added null-check.
// =============================================================================
import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';
import apiClient from '../services/apiClient';
import './DashboardPage.css';

interface DashStats {
  total_documents   : number;
  pending_approvals : number;
  ocr_queue         : number;
  total_users       : number;
}

interface RecentDoc {
  id          : number;
  title       : string;
  doc_number? : string;
  status      : string;
  updated_at  : string;
}

interface PendingApproval {
  id          : number;
  title       : string;
  doc_number? : string;
  created_by_name?: string;
  created_at  : string;
}

export default function DashboardPage() {
  const { user }  = useAuth();
  const navigate  = useNavigate();

  const [stats,    setStats]    = useState<DashStats | null>(null);
  const [recent,   setRecent]   = useState<RecentDoc[]>([]);
  const [pending,  setPending]  = useState<PendingApproval[]>([]);
  const [loading,  setLoading]  = useState(true);
  const [error,    setError]    = useState('');

  useEffect(() => {
    (async () => {
      try {
        const { data } = await apiClient.get('/dashboard/');
        setStats(data.stats ?? data);
        setRecent(data.recent_docs ?? []);
        setPending(data.pending_approvals ?? []);
      } catch {
        setError('Could not load dashboard data.');
      } finally {
        setLoading(false);
      }
    })();
  }, []);

  const STAT_CARDS = [
    { label: 'Total Documents',  value: stats?.total_documents,   icon: '📋', color: '#3b82f6', to: '/documents' },
    { label: 'Pending Approvals',value: stats?.pending_approvals, icon: '⏳',     color: '#f59e0b', to: '/documents?status=PENDING_REVIEW' },
    { label: 'OCR Queue',        value: stats?.ocr_queue,         icon: '🔍',     color: '#8b5cf6', to: '/ocr-queue' },
    { label: 'Total Users',      value: stats?.total_users,       icon: '👥',     color: '#10b981', to: null },
  ];

  const QUICK_LINKS = [
    { label: '⬆️ Upload Document', to: '/documents',     hint: 'Opens the documents list, then click Upload' },
    { label: '📤 New SDR',         to: '/sdr/new',       hint: 'Create a new Stores Demand Requisition' },
    { label: '🔍 OCR Queue',       to: '/ocr-queue',    hint: 'View OCR processing queue' },
    { label: '🔬 Prototype',       to: '/prototype-inspection', hint: 'Open prototype inspection module' },
    { label: '📂 PL Master',       to: '/pl-master',    hint: 'Open Parts List master' },
    { label: '📑 Work Ledger',     to: '/work-ledger',  hint: 'Open work ledger entries' },
  ];

  return (
    <div className="dash-page">
      {/* Header */}
      <div className="dash-header">
        <div>
          <h1 className="dash-title">Good {getGreeting()}, {user?.full_name?.split(' ')[0] ?? 'User'} 👋</h1>
          <p className="dash-subtitle">PLW EDMS — Locomotive Drawing Order Management</p>
        </div>
        <div className="dash-date">{new Date().toLocaleDateString('en-IN', { weekday:'long', year:'numeric', month:'long', day:'numeric' })}</div>
      </div>

      {error && <div className="dash-error">⚠️ {error}</div>}

      {/* Stat Cards */}
      <div className="dash-stats">
        {STAT_CARDS.map(c => (
          <div
            key={c.label}
            className={`dash-stat-card${c.to ? ' dash-stat-card--link' : ''}`}
            style={{ '--accent': c.color } as React.CSSProperties}
            onClick={() => c.to && navigate(c.to)}     // BUG FIX 1
          >
            <div className="dash-stat-icon">{c.icon}</div>
            <div className="dash-stat-body">
              <div className="dash-stat-val">{loading ? '—' : (c.value ?? 0)}</div>
              <div className="dash-stat-label">{c.label}</div>
            </div>
          </div>
        ))}
      </div>

      {/* Quick Links */}
      <div className="dash-section">
        <h2 className="dash-section-title">Quick Actions</h2>
        <div className="dash-quick-links">
          {QUICK_LINKS.map(lnk => (
            <button
              key={lnk.to}
              className="dash-quick-btn"
              title={lnk.hint}
              onClick={() => navigate(lnk.to)}          // BUG FIX 1: navigate not href
            >
              {lnk.label}
            </button>
          ))}
        </div>
      </div>

      {/* Two-column lower section */}
      <div className="dash-lower">
        {/* Recent Documents */}
        <div className="dash-card">
          <div className="dash-card-title">🕒 Recent Documents</div>
          {loading
            ? <div className="dash-center dash-muted">Loading…</div>
            : recent.length === 0
              ? <div className="dash-center dash-muted">No recent documents.</div>
              : (
                <table className="dash-table">
                  <thead><tr><th>Title</th><th>Status</th><th>Modified</th></tr></thead>
                  <tbody>
                    {recent.slice(0, 8).map(d => (
                      <tr key={d.id} className="dash-table-row" onClick={() => navigate(`/documents/${d.id}`)}>
                        <td className="dash-doc-title" title={d.title}>{d.title}</td>
                        <td><span className={`dash-badge dash-badge-${d.status?.toLowerCase()}`}>{d.status?.replace('_', ' ')}</span></td>
                        <td className="dash-muted" style={{ fontSize: 11 }}>{d.updated_at ? new Date(d.updated_at).toLocaleDateString('en-IN') : '\u2014'}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              )
          }
        </div>

        {/* Pending Approvals */}
        <div className="dash-card">
          <div className="dash-card-title">⏳ Pending Approvals</div>
          {loading
            ? <div className="dash-center dash-muted">Loading…</div>
            : (pending ?? []).length === 0   // BUG FIX 3: null-safe
              ? <div className="dash-center dash-muted">No pending approvals. ✅</div>
              : (
                <table className="dash-table">
                  <thead><tr><th>Document</th><th>Submitted By</th><th>Date</th></tr></thead>
                  <tbody>
                    {(pending ?? []).slice(0, 8).map(d => (
                      <tr key={d.id} className="dash-table-row" onClick={() => navigate(`/documents/${d.id}`)}>
                        <td className="dash-doc-title" title={d.title}>{d.title}</td>
                        <td className="dash-muted">{d.created_by_name ?? '\u2014'}</td>
                        <td className="dash-muted" style={{ fontSize: 11 }}>{d.created_at ? new Date(d.created_at).toLocaleDateString('en-IN') : '\u2014'}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              )
          }
        </div>

        <div className="dash-card">
          <div className="dash-card-title">⚡ Quick Actions</div>
          <div className="dash-quick-actions">
            <button className="dash-qa" onClick={() => navigate('/documents')}>📁 Browse Documents</button>
            <button className="dash-qa" onClick={() => navigate('/pl-master')}>📂 PL Master</button>
            <button className="dash-qa" onClick={() => navigate('/work-ledger')}>🗂️ Work Ledger</button>
            <button className="dash-qa" onClick={() => navigate('/bom')}>🔩 BOM Tree</button>
            <button className="dash-qa" onClick={() => navigate('/sdr')}>📤 SDR Register</button>
            <button className="dash-qa" onClick={() => navigate('/ocr-queue')}>🔍 OCR Queue</button>
            <button className="dash-qa" onClick={() => navigate('/audit')}>🛡️ Audit Logs</button>
            <button className="dash-qa" onClick={() => navigate('/search')}>🔎 Global Search</button>
          </div>
        </div>
      </div>
    </div>
  );
}

function getGreeting() {
  const h = new Date().getHours();
  if (h < 12) return 'morning';
  if (h < 17) return 'afternoon';
  return 'evening';
}

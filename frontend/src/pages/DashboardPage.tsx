// =============================================================================
// FILE: frontend/src/pages/DashboardPage.tsx  (Phase 2 — upgraded KPI + quick links)
// =============================================================================
import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { documentService } from '../services/documentService';
import { Btn } from '../components/common';
import './DashboardPage.css';

interface DashStats {
  documents: { total: number; active: number; draft: number; approved: number; obsolete: number };
  work_ledger: { open: number; in_progress: number; closed: number; on_hold: number };
  ocr_queue: { pending: number; processing: number; failed: number; completed: number };
  documents_by_section: { section__name: string; count: number }[];
  generated_at: string;
}

function KPICard({
  icon, label, value, sub, color = '#003366', onClick
}: { icon:string; label:string; value:number|string; sub?:string; color?:string; onClick?:()=>void }) {
  return (
    <div className={`kpi-card${onClick?' kpi-card--link':''}`} style={{ borderTopColor: color }} onClick={onClick}>
      <div className="kpi-icon">{icon}</div>
      <div className="kpi-value">{value}</div>
      <div className="kpi-label">{label}</div>
      {sub && <div className="kpi-sub">{sub}</div>}
    </div>
  );
}

export default function DashboardPage() {
  const [stats,   setStats]   = useState<DashStats|null>(null);
  const [loading, setLoading] = useState(true);
  const [error,   setError]   = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    documentService.dashboardStats()
      .then(setStats)
      .catch(() => setError(true))
      .finally(() => setLoading(false));
  }, []);

  if (loading) return (
    <div className="dash-loading">⏳ Loading dashboard…</div>
  );
  if (error || !stats) return (
    <div className="dash-error">
      <div className="dash-error-icon">⚠️</div>
      <h2>Could not load stats</h2>
      <p>Ensure the Django backend is running on LAN and the API is reachable.</p>
      <Btn onClick={() => window.location.reload()}>↺ Retry</Btn>
    </div>
  );

  const now = new Date(stats.generated_at);

  return (
    <div className="dash-page">
      {/* Header */}
      <div className="dash-header">
        <div>
          <h1 className="dash-title">Dashboard</h1>
          <p className="dash-sub">PLW Engineering Document Management — Live Overview</p>
        </div>
        <div className="dash-meta">
          <span>🕐 Updated: {now.toLocaleTimeString('en-IN')}</span>
          <Btn size="sm" variant="ghost" onClick={() => window.location.reload()}>↺ Refresh</Btn>
        </div>
      </div>

      {/* KPI Row 1 — Documents */}
      <div className="dash-section-label">📋 Documents</div>
      <div className="kpi-grid">
        <KPICard icon="📁" label="Total Documents" value={stats.documents.total}
          sub={`${stats.documents.active} active`} onClick={() => navigate('/documents')} />
        <KPICard icon="✅" label="Approved" value={stats.documents.approved}
          color="#059669" onClick={() => navigate('/documents?status=APPROVED')} />
        <KPICard icon="📝" label="Draft" value={stats.documents.draft}
          color="#d97706" sub="Pending approval" onClick={() => navigate('/documents?status=DRAFT')} />
        <KPICard icon="🗃️" label="Obsolete" value={stats.documents.obsolete}
          color="#6b7280" onClick={() => navigate('/documents?status=OBSOLETE')} />
      </div>

      {/* KPI Row 2 — Work Ledger */}
      <div className="dash-section-label">🗂️ Work Ledger</div>
      <div className="kpi-grid">
        <KPICard icon="🔴" label="Open" value={stats.work_ledger.open}
          color="#dc2626" onClick={() => navigate('/work-ledger?status=OPEN')} />
        <KPICard icon="🔵" label="In Progress" value={stats.work_ledger.in_progress}
          color="#2563eb" onClick={() => navigate('/work-ledger?status=IN_PROGRESS')} />
        <KPICard icon="⏸️" label="On Hold" value={stats.work_ledger.on_hold}
          color="#d97706" onClick={() => navigate('/work-ledger?status=ON_HOLD')} />
        <KPICard icon="✅" label="Closed" value={stats.work_ledger.closed}
          color="#059669" onClick={() => navigate('/work-ledger?status=CLOSED')} />
      </div>

      {/* KPI Row 3 — OCR Queue */}
      <div className="dash-section-label">🔍 OCR Queue</div>
      <div className="kpi-grid">
        <KPICard icon="⏳" label="Pending" value={stats.ocr_queue.pending}
          color="#d97706" onClick={() => navigate('/ocr-queue')} />
        <KPICard icon="⚙️" label="Processing" value={stats.ocr_queue.processing}
          color="#2563eb" onClick={() => navigate('/ocr-queue')} />
        <KPICard icon="❌" label="Failed" value={stats.ocr_queue.failed}
          color="#dc2626" sub="Needs review" onClick={() => navigate('/ocr-queue?status=FAILED')} />
        <KPICard icon="✅" label="Completed" value={stats.ocr_queue.completed}
          color="#059669" onClick={() => navigate('/ocr-queue?status=COMPLETED')} />
      </div>

      {/* Bottom row: sections table + quick actions */}
      <div className="dash-bottom">
        <div className="dash-card">
          <div className="dash-card-title">📊 Documents by Section</div>
          <table className="dash-table">
            <thead><tr><th>Section</th><th>Count</th></tr></thead>
            <tbody>
              {stats.documents_by_section.length === 0 &&
                <tr><td colSpan={2} style={{textAlign:'center',color:'#aaa',padding:16}}>No data</td></tr>}
              {stats.documents_by_section.map((row, i) => (
                <tr key={i}>
                  <td>{row.section__name ?? '(Unassigned)'}</td>
                  <td style={{textAlign:'right', fontWeight:700}}>{row.count}</td>
                </tr>
              ))}
            </tbody>
          </table>
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

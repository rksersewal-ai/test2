import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';
import { dashboardService } from '../services/dashboard';
import './DashboardPage.css';

interface DashStats {
  total_documents: number;
  pending_approvals: number;
  ocr_queue: number;
  total_users: number;
}

interface RecentDoc {
  id: number;
  title: string;
  doc_number?: string;
  status: string;
  updated_at: string;
}

interface PendingApproval {
  id: number;
  title: string;
  doc_number?: string;
  created_by_name?: string;
  created_at: string;
}

interface DashboardPayload {
  stats?: DashStats;
  recent_docs?: RecentDoc[];
  pending_approvals?: PendingApproval[];
  documents?: {
    total?: number;
  };
  ocr_queue?: {
    pending?: number;
    processing?: number;
    manual_review?: number;
  };
}

export default function DashboardPage() {
  const { user } = useAuth();
  const navigate = useNavigate();

  const [stats, setStats] = useState<DashStats | null>(null);
  const [recent, setRecent] = useState<RecentDoc[]>([]);
  const [pending, setPending] = useState<PendingApproval[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    (async () => {
      try {
        const data = (await dashboardService.stats()) as DashboardPayload;
        setStats(
          data.stats ?? {
            total_documents: data.documents?.total ?? 0,
            pending_approvals: data.pending_approvals?.length ?? 0,
            ocr_queue:
              (data.ocr_queue?.pending ?? 0)
              + (data.ocr_queue?.processing ?? 0)
              + (data.ocr_queue?.manual_review ?? 0),
            total_users: 0,
          }
        );
        setRecent(data.recent_docs ?? []);
        setPending(data.pending_approvals ?? []);
      } catch {
        setError('Could not load dashboard data.');
      } finally {
        setLoading(false);
      }
    })();
  }, []);

  const statCards = [
    { label: 'Total Documents', value: stats?.total_documents, color: '#3b82f6', to: '/documents' },
    { label: 'Pending Approvals', value: stats?.pending_approvals, color: '#f59e0b', to: '/documents' },
    { label: 'OCR Queue', value: stats?.ocr_queue, color: '#8b5cf6', to: '/ocr-queue' },
    { label: 'Total Users', value: stats?.total_users, color: '#10b981', to: null },
  ];

  const quickLinks = [
    { label: 'Upload Document', to: '/documents', hint: 'Open the documents list, then use Upload' },
    { label: 'New SDR', to: '/sdr/new', hint: 'Create a new Stores Demand Requisition' },
    { label: 'OCR Queue', to: '/ocr-queue', hint: 'View OCR processing queue' },
    { label: 'Prototype', to: '/prototype-inspection', hint: 'Open prototype inspection module' },
    { label: 'PL Master', to: '/pl-master', hint: 'Open Parts List master' },
    { label: 'Work Ledger', to: '/work-ledger', hint: 'Open work ledger entries' },
  ];

  return (
    <div className="dash-page">
      <div className="dash-header">
        <div>
          <h1 className="dash-title">Good {getGreeting()}, {user?.full_name?.split(' ')[0] ?? 'User'}</h1>
          <p className="dash-subtitle">PLW EDMS - Locomotive Drawing Order Management</p>
        </div>
        <div className="dash-date">
          {new Date().toLocaleDateString('en-IN', {
            weekday: 'long',
            year: 'numeric',
            month: 'long',
            day: 'numeric',
          })}
        </div>
      </div>

      {error && <div className="dash-error">{error}</div>}

      <div className="dash-stats">
        {statCards.map(card => (
          <div
            key={card.label}
            className={`dash-stat-card${card.to ? ' dash-stat-card--link' : ''}`}
            style={{ '--accent': card.color } as React.CSSProperties}
            onClick={() => card.to && navigate(card.to)}
          >
            <div className="dash-stat-body">
              <div className="dash-stat-val">{loading ? '-' : (card.value ?? 0)}</div>
              <div className="dash-stat-label">{card.label}</div>
            </div>
          </div>
        ))}
      </div>

      <div className="dash-section">
        <h2 className="dash-section-title">Quick Actions</h2>
        <div className="dash-quick-links">
          {quickLinks.map(link => (
            <button
              key={link.to}
              className="dash-quick-btn"
              title={link.hint}
              onClick={() => navigate(link.to)}
            >
              {link.label}
            </button>
          ))}
        </div>
      </div>

      <div className="dash-lower">
        <div className="dash-card">
          <div className="dash-card-title">Recent Documents</div>
          {loading ? (
            <div className="dash-center dash-muted">Loading...</div>
          ) : recent.length === 0 ? (
            <div className="dash-center dash-muted">No recent documents.</div>
          ) : (
            <table className="dash-table">
              <thead>
                <tr>
                  <th>Title</th>
                  <th>Status</th>
                  <th>Modified</th>
                </tr>
              </thead>
              <tbody>
                {recent.slice(0, 8).map(document => (
                  <tr key={document.id} className="dash-table-row" onClick={() => navigate(`/documents/${document.id}`)}>
                    <td className="dash-doc-title" title={document.title}>{document.title}</td>
                    <td>
                      <span className={`dash-badge dash-badge-${document.status?.toLowerCase()}`}>
                        {document.status?.replace('_', ' ')}
                      </span>
                    </td>
                    <td className="dash-muted" style={{ fontSize: 11 }}>
                      {document.updated_at ? new Date(document.updated_at).toLocaleDateString('en-IN') : '-'}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>

        <div className="dash-card">
          <div className="dash-card-title">Pending Approvals</div>
          {loading ? (
            <div className="dash-center dash-muted">Loading...</div>
          ) : pending.length === 0 ? (
            <div className="dash-center dash-muted">No pending approvals.</div>
          ) : (
            <table className="dash-table">
              <thead>
                <tr>
                  <th>Document</th>
                  <th>Submitted By</th>
                  <th>Date</th>
                </tr>
              </thead>
              <tbody>
                {pending.slice(0, 8).map(item => (
                  <tr key={`${item.id}-${item.created_at}`} className="dash-table-row" onClick={() => navigate(`/documents/${item.id}`)}>
                    <td className="dash-doc-title" title={item.title}>{item.title}</td>
                    <td className="dash-muted">{item.created_by_name ?? '-'}</td>
                    <td className="dash-muted" style={{ fontSize: 11 }}>
                      {item.created_at ? new Date(item.created_at).toLocaleDateString('en-IN') : '-'}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>

        <div className="dash-card">
          <div className="dash-card-title">Quick Links</div>
          <div className="dash-quick-actions">
            <button className="dash-qa" onClick={() => navigate('/documents')}>Browse Documents</button>
            <button className="dash-qa" onClick={() => navigate('/pl-master')}>PL Master</button>
            <button className="dash-qa" onClick={() => navigate('/work-ledger')}>Work Ledger</button>
            <button className="dash-qa" onClick={() => navigate('/bom')}>BOM Tree</button>
            <button className="dash-qa" onClick={() => navigate('/sdr')}>SDR Register</button>
            <button className="dash-qa" onClick={() => navigate('/ocr-queue')}>OCR Queue</button>
            <button className="dash-qa" onClick={() => navigate('/audit')}>Audit Logs</button>
            <button className="dash-qa" onClick={() => navigate('/search')}>Global Search</button>
          </div>
        </div>
      </div>
    </div>
  );
}

function getGreeting() {
  const hour = new Date().getHours();
  if (hour < 12) return 'morning';
  if (hour < 17) return 'afternoon';
  return 'evening';
}

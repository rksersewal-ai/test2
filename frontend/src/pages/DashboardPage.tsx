import { useDashboardStats } from '../hooks/useDashboard';
import '../components/Layout.css';

function StatCard({ label, value, sub, accent = false }: { label: string; value: number | string; sub?: string; accent?: boolean }) {
  return (
    <div className="card" style={{ borderTop: `3px solid ${accent ? 'var(--color-fuschia-100)' : 'var(--color-iris-80)'}` }}>
      <p style={{ fontSize: 'var(--font-size-sm)', color: 'var(--color-neutral-500)', marginBottom: 'var(--space-1)', fontWeight: 600 }}>{label}</p>
      <p style={{ fontSize: '2rem', fontWeight: 700, color: 'var(--color-neutral-900)', lineHeight: 1.1 }}>{value}</p>
      {sub && <p style={{ fontSize: 'var(--font-size-xs)', color: 'var(--color-neutral-500)', marginTop: 'var(--space-1)' }}>{sub}</p>}
    </div>
  );
}

export default function DashboardPage() {
  const { data: stats, isLoading, error } = useDashboardStats();

  if (isLoading) return <div className="empty-state"><h2>Loading dashboard\u2026</h2></div>;
  if (error || !stats) return <div className="empty-state"><h2>Could not load stats</h2><p>Ensure the backend is running on LAN.</p></div>;

  return (
    <div>
      <div className="page-header">
        <div>
          <h1 className="page-title">Dashboard</h1>
          <p className="page-subtitle">PLW Engineering Document Management System — Live Stats</p>
        </div>
        <span style={{ fontSize: 'var(--font-size-xs)', color: 'var(--color-neutral-500)' }}>
          Updated: {new Date(stats.generated_at).toLocaleTimeString('en-IN')}
        </span>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))', gap: 'var(--space-4)', marginBottom: 'var(--space-8)' }}>
        <StatCard label="Total Documents" value={stats.documents.total} sub={`${stats.documents.active} active`} />
        <StatCard label="Draft Documents" value={stats.documents.draft} sub="Pending approval" accent />
        <StatCard label="Open Work Items" value={stats.work_ledger.open} sub="Unassigned tasks" accent />
        <StatCard label="In Progress" value={stats.work_ledger.in_progress} sub="Work ledger" />
        <StatCard label="OCR Pending" value={stats.ocr_queue.pending} sub="Awaiting processing" />
        <StatCard label="OCR Failed" value={stats.ocr_queue.failed} sub="Needs review" accent />
      </div>

      <div className="card">
        <h2 style={{ marginBottom: 'var(--space-4)' }}>Documents by Section</h2>
        <div className="data-table-wrap">
          <table>
            <thead>
              <tr>
                <th>Section</th>
                <th>Document Count</th>
              </tr>
            </thead>
            <tbody>
              {stats.documents_by_section.length === 0 && (
                <tr><td colSpan={2} style={{ textAlign: 'center', color: 'var(--color-neutral-500)' }}>No data</td></tr>
              )}
              {stats.documents_by_section.map((row, i) => (
                <tr key={i}>
                  <td>{row.section__name ?? '(Unassigned)'}</td>
                  <td>{row.count}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}

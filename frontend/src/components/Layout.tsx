// =============================================================================
// FILE: frontend/src/components/Layout.tsx (Phase 1 — PL Master added to nav)
// =============================================================================
import { Outlet, NavLink, useNavigate } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';
import './Layout.css';

const NAV_GROUPS = [
  {
    group: 'Core',
    items: [
      { to: '/',       label: '📊 Dashboard', end: true },
      { to: '/search', label: '🔍 Search' },
    ],
  },
  {
    group: 'Documents',
    items: [
      { to: '/documents', label: '📋 Documents' },
      { to: '/sdr',       label: '📤 SDR Register' },
      { to: '/ocr-queue', label: '🔍 OCR Queue' },
    ],
  },
  {
    group: 'Engineering',
    items: [
      { to: '/pl-master',            label: '📂 PL Master' },
      { to: '/bom',                  label: '🔩 BOM' },
      { to: '/config',               label: '⚙️ Config Mgmt' },
      { to: '/prototype-inspection', label: '🔬 Prototype' },
      { to: '/master-data',          label: '🗃️ Master Data' },
    ],
  },
  {
    group: 'Operations',
    items: [
      { to: '/work-ledger', label: '🗂️ Work Ledger' },
    ],
  },
  {
    group: 'Admin',
    items: [
      { to: '/audit',    label: '🛡️ Audit Logs' },
      { to: '/settings', label: '⚙️ Settings' },
    ],
  },
];

export default function Layout() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const handleLogout = () => { logout(); navigate('/login'); };

  return (
    <div className="layout">
      <aside className="sidebar">
        <div className="sidebar-brand">
          <span className="brand-abbr">PLW</span>
          <span className="brand-text">LDO · EDMS</span>
        </div>
        <nav className="sidebar-nav">
          {NAV_GROUPS.map(group => (
            <div key={group.group} className="nav-group">
              <div className="nav-group-label">{group.group}</div>
              {group.items.map(n => (
                <NavLink key={n.to} to={n.to} end={n.end}
                  className={({ isActive }) => `nav-item${isActive?' nav-item--active':''}`}>
                  {n.label}
                </NavLink>
              ))}
            </div>
          ))}
        </nav>
        <div className="sidebar-footer">
          <div className="sidebar-user">
            <div className="user-avatar">{user?.full_name?.[0] ?? 'U'}</div>
            <div className="user-info">
              <span className="user-name">{user?.full_name}</span>
              <span className="user-role">{user?.role}</span>
            </div>
          </div>
          <button className="logout-btn" onClick={handleLogout} title="Logout">⇥ Logout</button>
        </div>
      </aside>
      <main className="main-content"><Outlet /></main>
    </div>
  );
}

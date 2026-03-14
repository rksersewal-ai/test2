// =============================================================================
// FILE: frontend/src/components/Layout.tsx
// BUG FIX: logout() is now async — handleLogout must await it before
// navigating to /login. Without await, navigate() ran before cookies
// were cleared server-side, causing immediate re-login from stale session.
// =============================================================================
import { Outlet, NavLink, useNavigate } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';
import './Layout.css';

const NAV_GROUPS = [
  {
    group: 'Core',
    items: [
      { to: '/',       label: '\u{1F4CA} Dashboard', end: true },
      { to: '/search', label: '\u{1F50D} Search' },
    ],
  },
  {
    group: 'Documents',
    items: [
      { to: '/documents', label: '\u{1F4CB} Documents' },
      { to: '/sdr',       label: '\u{1F4E4} SDR Register' },
      { to: '/ocr-queue', label: '\u{1F50D} OCR Queue' },
    ],
  },
  {
    group: 'Engineering',
    items: [
      { to: '/pl-master',            label: '\u{1F4C2} PL Master' },
      { to: '/bom',                  label: '\u{1F529} BOM' },
      { to: '/config',               label: '\u2699\uFE0F Config Mgmt' },
      { to: '/prototype-inspection', label: '\u{1F52C} Prototype' },
      { to: '/master-data',          label: '\u{1F5C3}\uFE0F Master Data' },
    ],
  },
  {
    group: 'Operations',
    items: [
      { to: '/work-ledger', label: '\u{1F5C2}\uFE0F Work Ledger' },
    ],
  },
  {
    group: 'Admin',
    items: [
      { to: '/audit',    label: '\u{1F6E1}\uFE0F Audit Logs' },
      { to: '/settings', label: '\u2699\uFE0F Settings' },
    ],
  },
];

export default function Layout() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  // BUG FIX: must await async logout() before navigating
  const handleLogout = async () => {
    try {
      await logout();
    } finally {
      navigate('/login', { replace: true });
    }
  };

  return (
    <div className="layout">
      <aside className="sidebar">
        <div className="sidebar-brand">
          <span className="brand-abbr">PLW</span>
          <span className="brand-text">LDO \u00B7 EDMS</span>
        </div>
        <nav className="sidebar-nav">
          {NAV_GROUPS.map(group => (
            <div key={group.group} className="nav-group">
              <div className="nav-group-label">{group.group}</div>
              {group.items.map(n => (
                <NavLink
                  key={n.to}
                  to={n.to}
                  end={'end' in n ? (n as {end?: boolean}).end : false}
                  className={({ isActive }) =>
                    `nav-item${isActive ? ' nav-item--active' : ''}`
                  }
                >
                  {n.label}
                </NavLink>
              ))}
            </div>
          ))}
        </nav>
        <div className="sidebar-footer">
          <div className="sidebar-user">
            <div className="user-avatar">
              {user?.full_name?.[0]?.toUpperCase() ?? 'U'}
            </div>
            <div className="user-info">
              <span className="user-name">{user?.full_name ?? 'User'}</span>
              <span className="user-role">{user?.role ?? ''}</span>
            </div>
          </div>
          <button
            className="logout-btn"
            onClick={handleLogout}
            title="Logout"
          >
            \u21A5 Logout
          </button>
        </div>
      </aside>
      <main className="main-content">
        <Outlet />
      </main>
    </div>
  );
}

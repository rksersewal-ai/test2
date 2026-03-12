import { Outlet, NavLink, useNavigate } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';
import './Layout.css';

const NAV = [
  { to: '/', label: '\uD83D\uDCCA Dashboard', end: true },
  { to: '/documents', label: '\uD83D\uDCCB Documents' },
  { to: '/work-ledger', label: '\uD83D\uDDC2\uFE0F Work Ledger' },
  { to: '/ocr-queue', label: '\uD83D\uDD0D OCR Queue' },
  { to: '/audit', label: '\uD83D\uDEE1\uFE0F Audit Logs' },
];

export default function Layout() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <div className="layout">
      <aside className="sidebar">
        <div className="sidebar-brand">
          <span className="brand-abbr">PLW</span>
          <span className="brand-text">EDMS</span>
        </div>
        <nav className="sidebar-nav">
          {NAV.map((n) => (
            <NavLink
              key={n.to}
              to={n.to}
              end={n.end}
              className={({ isActive }) => `nav-item${isActive ? ' nav-item--active' : ''}`}
            >
              {n.label}
            </NavLink>
          ))}
        </nav>
        <div className="sidebar-user">
          <div className="user-avatar">{user?.full_name?.[0] ?? 'U'}</div>
          <div className="user-info">
            <span className="user-name">{user?.full_name}</span>
            <span className="user-role">{user?.role}</span>
          </div>
          <button className="logout-btn" onClick={handleLogout} title="Logout">\u21A6</button>
        </div>
      </aside>
      <main className="main-content">
        <Outlet />
      </main>
    </div>
  );
}

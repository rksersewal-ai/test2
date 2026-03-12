/**
 * AppLayout — Enterprise shell: sidebar + header + content
 * Sidebar: 240px, collapsible to 56px icon-only mode
 * Header: 48px, includes breadcrumb, text-scale A+/A-/Reset controls
 */
import { useState, ReactNode } from 'react';
import { NavLink, Outlet, useNavigate } from 'react-router-dom';
import { useTextScale } from '../context/TextScaleContext';
import { useAuth } from '../hooks/useAuth';
import './AppLayout.css';

const NAV_ITEMS = [
  { to: '/',           label: 'Dashboard',    icon: '\u{1F4CA}', end: true },
  { to: '/documents',  label: 'Documents',    icon: '\u{1F4CB}' },
  { to: '/work-ledger',label: 'Work Ledger',  icon: '\uD83D\uDDC2\uFE0F' },
  { to: '/ocr-queue',  label: 'OCR Queue',    icon: '\uD83D\uDD0D' },
  { to: '/audit',      label: 'Audit Logs',   icon: '\uD83D\uDEE1\uFE0F' },
];

export function AppLayout() {
  const [collapsed, setCollapsed] = useState(false);
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const { level, increase, decrease, reset } = useTextScale();

  return (
    <div className={`app-shell${collapsed ? ' sidebar-collapsed' : ''}`}>
      {/* ---- SIDEBAR ---- */}
      <aside className="app-sidebar" aria-label="Main navigation">
        <div className="sidebar-brand">
          {!collapsed && (
            <>
              <span className="brand-chip">PLW</span>
              <span className="brand-name">EDMS</span>
            </>
          )}
          {collapsed && <span className="brand-chip">P</span>}
        </div>

        <nav className="sidebar-nav">
          {NAV_ITEMS.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              end={item.end}
              className={({ isActive }) => `nav-link${isActive ? ' nav-link--active' : ''}`}
              title={collapsed ? item.label : undefined}
            >
              <span className="nav-icon" aria-hidden>{item.icon}</span>
              {!collapsed && <span className="nav-label">{item.label}</span>}
            </NavLink>
          ))}
        </nav>

        <div className="sidebar-footer">
          <div className="sidebar-user" title={`${user?.full_name} — ${user?.role}`}>
            <div className="user-avatar">{user?.full_name?.[0] ?? 'U'}</div>
            {!collapsed && (
              <div className="user-meta">
                <span className="user-name">{user?.full_name}</span>
                <span className="user-role">{user?.role}</span>
              </div>
            )}
          </div>
          {!collapsed && (
            <button className="btn-ghost-icon" title="Logout"
              onClick={() => { logout(); navigate('/login'); }}>
              &#8594;
            </button>
          )}
        </div>
      </aside>

      {/* ---- MAIN COLUMN ---- */}
      <div className="app-main">
        {/* HEADER */}
        <header className="app-header" role="banner">
          <button
            className="collapse-btn"
            onClick={() => setCollapsed((c) => !c)}
            aria-label="Toggle sidebar"
          >
            {collapsed ? '\u2630' : '\u2630'}
          </button>

          <span className="header-app-name">Engineering Document Management System</span>
          <span className="header-org">Patiala Locomotive Works</span>

          <div className="header-right">
            {/* A+ / A- / Reset text scale controls */}
            <div className="text-scale-controls" role="group" aria-label="Text size controls">
              <button className={`scale-btn${level === 'small' ? ' active' : ''}`}
                onClick={decrease} title="Decrease text size" aria-label="Decrease text size">
                A⁻
              </button>
              <button className={`scale-btn${level === 'default' ? ' active' : ''}`}
                onClick={reset} title="Reset text size" aria-label="Reset text size">
                A
              </button>
              <button className={`scale-btn${level === 'large' || level === 'xlarge' ? ' active' : ''}`}
                onClick={increase} title="Increase text size" aria-label="Increase text size">
                A⁺
              </button>
            </div>

            <span className="header-username">{user?.username}</span>
          </div>
        </header>

        {/* CONTENT */}
        <main className="app-content" id="main-content">
          <Outlet />
        </main>
      </div>
    </div>
  );
}

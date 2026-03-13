// =============================================================================
// FILE: frontend/src/components/notifications/NotificationBell.tsx
// SPRINT 4 — In-App Notification Bell (header icon + dropdown)
// Shows unread badge count. Dropdown lists last 10 notifications.
// Marks individual notifications read on click; "Mark all read" button.
// Reconnects SSE on EOF (4-min cycle).
// =============================================================================
import React, { useEffect, useRef, useState } from 'react';
import { useNotifications } from '../../hooks/useNotifications';

const KIND_ICON: Record<string, string> = {
  INFO:                'ℹ️',
  SUCCESS:             '✅',
  WARNING:             '⚠️',
  ERROR:               '🔴',
  APPROVAL_REQUESTED:  '📝',
  APPROVAL_APPROVED:   '✅',
  APPROVAL_REJECTED:   '❌',
  OVERDUE_WORK:        '⏰',
  OCR_COMPLETE:        '🔍',
  OCR_FAILED:          '🚨',
  DOCUMENT_PUBLISHED:  '📌',
  MENTION:             '💬',
};

interface Props {
  onNavigate: (path: string) => void;
}

export const NotificationBell: React.FC<Props> = ({ onNavigate }) => {
  const [open, setOpen] = useState(false);
  const panelRef        = useRef<HTMLDivElement>(null);
  const {
    notifications, unreadCount,
    markRead, markAllRead, reload,
  } = useNotifications();

  // Close on outside click
  useEffect(() => {
    const handler = (e: MouseEvent) => {
      if (panelRef.current && !panelRef.current.contains(e.target as Node)) {
        setOpen(false);
      }
    };
    document.addEventListener('mousedown', handler);
    return () => document.removeEventListener('mousedown', handler);
  }, []);

  // SSE reconnect loop
  useEffect(() => {
    let es: EventSource;
    const connect = () => {
      es = new EventSource('/api/notifications/stream/');
      es.onmessage = (e) => {
        const data = JSON.parse(e.data);
        if (data.eof) { es.close(); connect(); return; }  // reconnect
        reload();
      };
      es.onerror = () => { es.close(); setTimeout(connect, 5000); };
    };
    connect();
    return () => es?.close();
  }, [reload]);

  const handleClick = async (notif: { id: number; is_read: boolean; action_url: string }) => {
    if (!notif.is_read) await markRead(notif.id);
    setOpen(false);
    if (notif.action_url) onNavigate(notif.action_url);
  };

  return (
    <div className="notif-bell" ref={panelRef}>
      <button
        className={`notif-bell__btn${unreadCount > 0 ? ' notif-bell__btn--active' : ''}`}
        onClick={() => setOpen(o => !o)}
        aria-label={`Notifications (${unreadCount} unread)`}
        aria-expanded={open}
        aria-haspopup="true"
      >
        🔔
        {unreadCount > 0 && (
          <span className="notif-bell__badge" aria-hidden>
            {unreadCount > 99 ? '99+' : unreadCount}
          </span>
        )}
      </button>

      {open && (
        <div className="notif-panel" role="dialog" aria-label="Notifications">
          <div className="notif-panel__header">
            <span className="notif-panel__title">Notifications</span>
            {unreadCount > 0 && (
              <button
                className="notif-panel__mark-all"
                onClick={() => markAllRead()}
              >
                Mark all read
              </button>
            )}
          </div>

          {notifications.length === 0 ? (
            <p className="notif-panel__empty">No notifications yet.</p>
          ) : (
            <ul className="notif-panel__list">
              {notifications.map(n => (
                <li
                  key={n.id}
                  className={`notif-panel__item${
                    !n.is_read ? ' notif-panel__item--unread' : ''
                  }`}
                >
                  <button
                    className="notif-panel__item-btn"
                    onClick={() => handleClick(n)}
                  >
                    <span className="notif-panel__kind-icon">
                      {KIND_ICON[n.kind] ?? '•'}
                    </span>
                    <div className="notif-panel__item-content">
                      <span className="notif-panel__item-title">{n.title}</span>
                      {n.body && (
                        <span className="notif-panel__item-body">{n.body}</span>
                      )}
                      <span className="notif-panel__item-time">
                        {new Date(n.created_at).toLocaleString('en-IN', {
                          day: '2-digit', month: 'short',
                          hour: '2-digit', minute: '2-digit',
                        })}
                      </span>
                    </div>
                  </button>
                </li>
              ))}
            </ul>
          )}
        </div>
      )}
    </div>
  );
};

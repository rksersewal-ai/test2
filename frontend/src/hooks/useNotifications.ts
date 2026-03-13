// =============================================================================
// FILE: frontend/src/hooks/useNotifications.ts
// SPRINT 4 — Notification inbox hook
// =============================================================================
import { useState, useEffect, useCallback } from 'react';

export interface NotificationItem {
  id:          number;
  kind:        string;
  title:       string;
  body:        string;
  action_url:  string;
  is_read:     boolean;
  created_at:  string;
}

interface UseNotificationsResult {
  notifications: NotificationItem[];
  unreadCount:   number;
  loading:       boolean;
  markRead:      (id: number)  => Promise<void>;
  markAllRead:   ()            => Promise<void>;
  reload:        ()            => void;
}

export function useNotifications(): UseNotificationsResult {
  const [notifications, setNotifications] = useState<NotificationItem[]>([]);
  const [unreadCount,   setUnreadCount]   = useState(0);
  const [loading,       setLoading]       = useState(true);
  const [tick,          setTick]          = useState(0);

  const reload = useCallback(() => setTick(t => t + 1), []);

  useEffect(() => {
    setLoading(true);
    Promise.all([
      fetch('/api/notifications/?unread=false', { credentials: 'include' })
        .then(r => r.json()),
      fetch('/api/notifications/unread-count/', { credentials: 'include' })
        .then(r => r.json()),
    ])
      .then(([list, countData]) => {
        setNotifications(Array.isArray(list) ? list : list.results ?? []);
        setUnreadCount(countData.count ?? 0);
      })
      .catch(() => {})
      .finally(() => setLoading(false));
  }, [tick]);

  const markRead = useCallback(async (id: number) => {
    await fetch(`/api/notifications/${id}/read/`, {
      method: 'POST', credentials: 'include',
    });
    reload();
  }, [reload]);

  const markAllRead = useCallback(async () => {
    await fetch('/api/notifications/read-all/', {
      method: 'POST', credentials: 'include',
    });
    reload();
  }, [reload]);

  return { notifications, unreadCount, loading, markRead, markAllRead, reload };
}

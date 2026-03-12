import React, { createContext, useCallback, useContext, useState } from 'react';
import type { PreviewTab } from '../types/preview';

interface PreviewTabsCtx {
  tabs: PreviewTab[];
  activeTabId: string | null;
  openTab: (tab: PreviewTab) => void;
  closeTab: (id: string) => void;
  setActiveTab: (id: string) => void;
}

const Ctx = createContext<PreviewTabsCtx | null>(null);

export function PreviewTabsProvider({ children }: { children: React.ReactNode }) {
  const [tabs, setTabs] = useState<PreviewTab[]>([]);
  const [activeTabId, setActiveTabId] = useState<string | null>(null);

  const openTab = useCallback((tab: PreviewTab) => {
    setTabs(prev => {
      const exists = prev.find(t => t.id === tab.id);
      if (exists) return prev;
      return [...prev, tab];
    });
    setActiveTabId(tab.id);
  }, []);

  const closeTab = useCallback((id: string) => {
    setTabs(prev => {
      const next = prev.filter(t => t.id !== id);
      return next;
    });
    setActiveTabId(prev => {
      if (prev !== id) return prev;
      const remaining = tabs.filter(t => t.id !== id);
      return remaining.length > 0 ? remaining[remaining.length - 1].id : null;
    });
  }, [tabs]);

  return (
    <Ctx.Provider value={{ tabs, activeTabId, openTab, closeTab, setActiveTab: setActiveTabId }}>
      {children}
    </Ctx.Provider>
  );
}

export function usePreviewTabs() {
  const ctx = useContext(Ctx);
  if (!ctx) throw new Error('usePreviewTabs must be used within PreviewTabsProvider');
  return ctx;
}

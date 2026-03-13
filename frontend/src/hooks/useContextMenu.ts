import { useState, useCallback } from 'react';
import { ContextMenuAction } from '../components/ContextMenu';

interface ContextMenuState {
  x: number;
  y: number;
  visible: boolean;
  actions: ContextMenuAction[];
  title?: string;
}

export function useContextMenu() {
  const [menu, setMenu] = useState<ContextMenuState>({
    x: 0,
    y: 0,
    visible: false,
    actions: [],
    title: undefined,
  });

  const openMenu = useCallback(
    (e: React.MouseEvent, actions: ContextMenuAction[], title?: string) => {
      e.preventDefault();
      e.stopPropagation();
      setMenu({ x: e.clientX, y: e.clientY, visible: true, actions, title });
    },
    []
  );

  const closeMenu = useCallback(() => {
    setMenu(prev => ({ ...prev, visible: false }));
  }, []);

  return { menu, openMenu, closeMenu };
}

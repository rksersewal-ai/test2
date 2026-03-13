import { useEffect } from 'react';

type Modifier = 'ctrl' | 'shift' | 'alt' | 'meta';

export function useKeyboardShortcut(
  key: string,
  callback: () => void,
  modifiers: Modifier[] = []
) {
  useEffect(() => {
    const handler = (e: KeyboardEvent) => {
      const ctrlOk = modifiers.includes('ctrl') ? e.ctrlKey : !e.ctrlKey;
      const shiftOk = modifiers.includes('shift') ? e.shiftKey : !e.shiftKey;
      const altOk = modifiers.includes('alt') ? e.altKey : !e.altKey;
      const metaOk = modifiers.includes('meta') ? e.metaKey : !e.metaKey;
      if (e.key === key && ctrlOk && shiftOk && altOk && metaOk) {
        e.preventDefault();
        callback();
      }
    };
    window.addEventListener('keydown', handler);
    return () => window.removeEventListener('keydown', handler);
  }, [key, callback, modifiers]);
}

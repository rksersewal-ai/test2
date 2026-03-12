/**
 * useRowSelection — row multi-select state manager for DataTable
 */
import { useState, useCallback } from 'react';

export function useRowSelection<T extends string | number>() {
  const [selected, setSelected] = useState<Set<T>>(new Set());

  const toggle = useCallback((key: T) => {
    setSelected((prev) => {
      const next = new Set(prev);
      if (next.has(key)) next.delete(key); else next.add(key);
      return next;
    });
  }, []);

  const setAll = useCallback((keys: T[]) => {
    setSelected(new Set(keys));
  }, []);

  const clear = useCallback(() => setSelected(new Set()), []);

  return { selected, toggle, setAll, clear };
}

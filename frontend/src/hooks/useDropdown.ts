// =============================================================================
// FILE: frontend/src/hooks/useDropdown.ts
// PURPOSE: Hook to fetch + cache dropdown items for a group, sorted alphabetically.
// Usage:  const { items, loading } = useDropdown('section');
// =============================================================================
import { useEffect, useState, useRef } from 'react';
import { dropdownApi } from '../services/dropdownApi';
import type { DropdownItem } from '../types/dropdown';

// Simple module-level cache: avoids repeated API calls for same group in same session
const cache: Record<string, DropdownItem[]> = {};

export function useDropdown(groupKey: string) {
  const [items, setItems] = useState<DropdownItem[]>(cache[groupKey] ?? []);
  const [loading, setLoading] = useState(!cache[groupKey]);
  const [error, setError] = useState<string | null>(null);
  const mounted = useRef(true);

  useEffect(() => {
    mounted.current = true;
    if (cache[groupKey]) {
      setItems(cache[groupKey]);
      setLoading(false);
      return;
    }
    setLoading(true);
    dropdownApi
      .getGroup(groupKey)
      .then((data) => {
        // Sort alphabetically by label; honour sort_override first
        const sorted = [...data].sort((a, b) => {
          const aSort = a.sort_override ?? Infinity;
          const bSort = b.sort_override ?? Infinity;
          if (aSort !== bSort) return aSort - bSort;
          return a.label.localeCompare(b.label);
        });
        cache[groupKey] = sorted;
        if (mounted.current) setItems(sorted);
      })
      .catch((e) => { if (mounted.current) setError(e.message); })
      .finally(() => { if (mounted.current) setLoading(false); });
    return () => { mounted.current = false; };
  }, [groupKey]);

  const invalidate = () => { delete cache[groupKey]; };

  return { items, loading, error, invalidate };
}

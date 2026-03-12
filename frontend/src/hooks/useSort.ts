/**
 * useSort — sortable column state manager
 * Returns { sortKey, sortDir, handleSort } and a sorted copy of data.
 */
import { useState, useMemo } from 'react';
import type { SortDirection } from '../components/DataTable';

export function useSort<T>(
  data: T[],
  getValue: (row: T, key: string) => unknown = (r, k) => (r as Record<string, unknown>)[k]
) {
  const [sortKey, setSortKey] = useState<string>('');
  const [sortDir, setSortDir] = useState<SortDirection>(null);

  const handleSort = (key: string) => {
    if (sortKey !== key) { setSortKey(key); setSortDir('asc'); }
    else if (sortDir === 'asc') setSortDir('desc');
    else { setSortKey(''); setSortDir(null); }
  };

  const sorted = useMemo(() => {
    if (!sortKey || !sortDir) return data;
    return [...data].sort((a, b) => {
      const av = getValue(a, sortKey);
      const bv = getValue(b, sortKey);
      const cmp = String(av ?? '').localeCompare(String(bv ?? ''), 'en-IN', { numeric: true, sensitivity: 'base' });
      return sortDir === 'asc' ? cmp : -cmp;
    });
  }, [data, sortKey, sortDir, getValue]);

  return { sortKey, sortDir, handleSort, sorted };
}

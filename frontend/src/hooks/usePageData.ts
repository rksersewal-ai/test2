import { useState, useEffect, useCallback } from 'react';

export interface PageDataOptions<T> {
  fetchFn: () => Promise<T>;
  deps?: unknown[];
  initialData?: T | null;
}

export interface PageDataState<T> {
  data: T | null;
  loading: boolean;
  error: string | null;
  refetch: () => void;
}

/**
 * Generic page data hook — wraps any async fetch with
 * loading / error / refetch state for all EDMS pages.
 */
export function usePageData<T>(options: PageDataOptions<T>): PageDataState<T> {
  const { fetchFn, deps = [], initialData = null } = options;
  const [data, setData] = useState<T | null>(initialData);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [tick, setTick] = useState(0);

  const refetch = useCallback(() => setTick(t => t + 1), []);

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    setError(null);
    fetchFn()
      .then(result => {
        if (!cancelled) {
          setData(result);
          setLoading(false);
        }
      })
      .catch(err => {
        if (!cancelled) {
          setError(err?.message ?? 'Failed to load data');
          setLoading(false);
        }
      });
    return () => { cancelled = true; };
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [tick, ...deps]);

  return { data, loading, error, refetch };
}

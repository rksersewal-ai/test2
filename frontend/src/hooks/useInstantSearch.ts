/**
 * FILE: frontend/src/hooks/useInstantSearch.ts
 *
 * React hook that powers Everything-style instant search against
 * GET /api/v1/search/autocomplete/  (typeahead dropdown)
 * GET /api/v1/search/unified/       (full result page)
 *
 * PRODUCTION SAFETY:
 *   - 250 ms debounce prevents an API call on every keystroke
 *   - AbortController cancels in-flight requests when query changes,
 *     preventing race-condition stale results from appearing
 *   - Minimum 2-char guard matches backend enforcement
 *   - Errors set an `error` state string — UI can show a non-blocking
 *     message rather than crashing
 *   - isLoading flag allows the UI to show a spinner without blocking input
 *
 * USAGE EXAMPLE:
 *
 *   const { suggestions, loading, error } = useInstantSearch(inputValue);
 *
 *   // Typeahead dropdown:
 *   {suggestions.map(s => (
 *     <div key={s.id} onClick={() => navigate(`/documents/${s.id}`)}>
 *       <strong>{s.document_number}</strong> — {s.title}
 *       {s.file_name && <span className="badge">{s.file_name}</span>}
 *       <span className="source-badge">{s.match_source}</span>
 *     </div>
 *   ))}
 *
 *   // Full search page (pass submitQuery separately):
 *   const { results, count, pages } = useUnifiedSearch(submittedQuery, page);
 */

import { useState, useEffect, useRef, useCallback } from 'react';

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

export interface SearchSuggestion {
  id:              number;
  document_number: string;
  title:           string;
  status:          string;
  file_name:       string | null;
  file_type:       string | null;
  match_source:    'document' | 'filename';
  rank:            number;
}

export interface UnifiedResult {
  id:              number;
  document_number: string;
  title:           string;
  status:          string;
  file_name:       string | null;
  file_type:       string | null;
  match_source:    'doc_number' | 'title' | 'filename' | 'ocr_text' | 'note' | 'correspondent';
  snippet:         string | null;
  rank:            number;
}

export interface UnifiedSearchResponse {
  count:     number;
  page:      number;
  pages:     number;
  page_size: number;
  results:   UnifiedResult[];
}

// ---------------------------------------------------------------------------
// Constants
// ---------------------------------------------------------------------------

const DEBOUNCE_MS    = 250;
const MIN_QUERY_LEN  = 2;
const API_BASE       = '/api/v1/search';

// ---------------------------------------------------------------------------
// Utility: debounce
// ---------------------------------------------------------------------------

function useDebounce<T>(value: T, delay: number): T {
  const [debounced, setDebounced] = useState<T>(value);
  useEffect(() => {
    const timer = setTimeout(() => setDebounced(value), delay);
    return () => clearTimeout(timer);
  }, [value, delay]);
  return debounced;
}

// ---------------------------------------------------------------------------
// Hook 1: useInstantSearch  — typeahead autocomplete
// ---------------------------------------------------------------------------

export function useInstantSearch(
  query: string,
  limit  = 10,
) {
  const [suggestions, setSuggestions] = useState<SearchSuggestion[]>([]);
  const [loading,     setLoading]     = useState(false);
  const [error,       setError]       = useState<string | null>(null);
  const abortRef                      = useRef<AbortController | null>(null);
  const debouncedQuery                = useDebounce(query.trim(), DEBOUNCE_MS);

  useEffect(() => {
    // Cancel any previous in-flight request
    abortRef.current?.abort();

    if (debouncedQuery.length < MIN_QUERY_LEN) {
      setSuggestions([]);
      setError(null);
      return;
    }

    const controller    = new AbortController();
    abortRef.current    = controller;
    setLoading(true);
    setError(null);

    const url = `${API_BASE}/autocomplete/?q=${encodeURIComponent(debouncedQuery)}&limit=${limit}`;

    fetch(url, {
      credentials: 'include',          // send JWT cookie
      signal:      controller.signal,
    })
      .then(async res => {
        if (!res.ok) {
          const body = await res.json().catch(() => ({}));
          throw new Error(body?.error ?? `HTTP ${res.status}`);
        }
        return res.json() as Promise<SearchSuggestion[]>;
      })
      .then(data => {
        setSuggestions(data);
        setLoading(false);
      })
      .catch(err => {
        if (err.name === 'AbortError') return;  // Intentional cancel — ignore
        setError(err.message ?? 'Search unavailable');
        setSuggestions([]);
        setLoading(false);
      });

    return () => controller.abort();
  }, [debouncedQuery, limit]);

  return { suggestions, loading, error };
}

// ---------------------------------------------------------------------------
// Hook 2: useUnifiedSearch  — full paginated search results page
// ---------------------------------------------------------------------------

export function useUnifiedSearch(
  query:    string,
  page      = 1,
  pageSize  = 25,
) {
  const [data,    setData]    = useState<UnifiedSearchResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error,   setError]   = useState<string | null>(null);
  const abortRef              = useRef<AbortController | null>(null);

  // Unified search is triggered by explicit submit (Enter / search button),
  // so we do NOT debounce here — the query is already committed.
  const fetchResults = useCallback(() => {
    abortRef.current?.abort();

    if (query.trim().length < MIN_QUERY_LEN) {
      setData(null);
      return;
    }

    const controller = new AbortController();
    abortRef.current = controller;
    setLoading(true);
    setError(null);

    const url = (
      `${API_BASE}/unified/?q=${encodeURIComponent(query.trim())}` +
      `&page=${page}&page_size=${pageSize}`
    );

    fetch(url, {
      credentials: 'include',
      signal:      controller.signal,
    })
      .then(async res => {
        if (!res.ok) {
          const body = await res.json().catch(() => ({}));
          throw new Error(body?.error ?? `HTTP ${res.status}`);
        }
        return res.json() as Promise<UnifiedSearchResponse>;
      })
      .then(json => {
        setData(json);
        setLoading(false);
      })
      .catch(err => {
        if (err.name === 'AbortError') return;
        setError(err.message ?? 'Search unavailable');
        setData(null);
        setLoading(false);
      });

    return () => controller.abort();
  }, [query, page, pageSize]);

  useEffect(() => {
    const cleanup = fetchResults();
    return cleanup ?? undefined;
  }, [fetchResults]);

  return {
    results:  data?.results  ?? [],
    count:    data?.count    ?? 0,
    pages:    data?.pages    ?? 0,
    page_size: data?.page_size ?? pageSize,
    loading,
    error,
    refetch:  fetchResults,
  };
}

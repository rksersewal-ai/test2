// =============================================================================
// FILE: frontend/src/hooks/useSimilarDocuments.ts
// SPRINT 2 — Feature #8
// PURPOSE : Fetches similar documents for a given document ID.
// =============================================================================
import { useState, useEffect } from 'react';

export interface SimilarDoc {
  id: number;
  document_number: string;
  title: string;
  status: string;
  category_name: string;
  document_type_name: string;
  similarity_score: number;
}

interface SimilarDocsResponse {
  source_id:    number;
  source_title: string;
  count:        number;
  results:      SimilarDoc[];
}

interface UseSimilarDocumentsResult {
  results:     SimilarDoc[];
  loading:     boolean;
  sourceTitle: string;
  reload:      () => void;
}

export function useSimilarDocuments(
  documentId: number,
  limit = 5,
  threshold?: number,
): UseSimilarDocumentsResult {
  const [results,     setResults]     = useState<SimilarDoc[]>([]);
  const [loading,     setLoading]     = useState(true);
  const [sourceTitle, setSourceTitle] = useState('');
  const [tick,        setTick]        = useState(0);

  const reload = () => setTick(t => t + 1);

  useEffect(() => {
    if (!documentId) return;
    setLoading(true);
    let url = `/api/edms/documents/${documentId}/similar/?limit=${limit}`;
    if (threshold !== undefined) url += `&threshold=${threshold}`;

    fetch(url, { credentials: 'include' })
      .then(r => r.json())
      .then((data: SimilarDocsResponse) => {
        setResults(data.results ?? []);
        setSourceTitle(data.source_title ?? '');
      })
      .catch(() => setResults([]))
      .finally(() => setLoading(false));
  }, [documentId, limit, threshold, tick]);

  return { results, loading, sourceTitle, reload };
}

// =============================================================================
// FILE: frontend/src/hooks/useClassifier.ts
// SPRINT 5 — ML Classifier hook
//
// Calls POST /api/ml/results/classify/{documentId}/
// Returns predictions per target, loading state, and accept/override/reject actions.
// =============================================================================
import { useState, useCallback } from 'react';

export interface Prediction {
  label:      string;
  label_id:   number;
  confidence: number;
}

export interface ClassificationPredictions {
  document_type:  Prediction[];
  category:       Prediction[];
  correspondent:  Prediction[];
}

export interface ClassificationResult {
  id:              number;
  target:          string;
  predictions:     Prediction[];
  top_label:       string;
  top_confidence:  number;
  outcome:         'PENDING' | 'ACCEPTED' | 'OVERRIDDEN' | 'REJECTED';
}

interface UseClassifierResult {
  predictions:  ClassificationPredictions | null;
  results:      ClassificationResult[];
  loading:      boolean;
  error:        string | null;
  classify:     (documentId: number) => Promise<void>;
  accept:       (resultId: number) => Promise<void>;
  override:     (resultId: number, labelId: number) => Promise<void>;
  reject:       (resultId: number) => Promise<void>;
  loadResults:  (documentId: number) => Promise<void>;
}

export function useClassifier(): UseClassifierResult {
  const [predictions, setPredictions] = useState<ClassificationPredictions | null>(null);
  const [results,     setResults]     = useState<ClassificationResult[]>([]);
  const [loading,     setLoading]     = useState(false);
  const [error,       setError]       = useState<string | null>(null);

  const classify = useCallback(async (documentId: number) => {
    setLoading(true);
    setError(null);
    try {
      const res  = await fetch(`/api/ml/results/classify/${documentId}/`, {
        method: 'POST', credentials: 'include',
      });
      const data = await res.json();
      if (!res.ok) { setError(data.error ?? 'Classification failed'); return; }
      setPredictions(data);
    } catch (e: any) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  }, []);

  const loadResults = useCallback(async (documentId: number) => {
    const res  = await fetch(`/api/ml/results/?document=${documentId}`, {
      credentials: 'include',
    });
    const data = await res.json();
    setResults(Array.isArray(data) ? data : data.results ?? []);
  }, []);

  const _reviewAction = useCallback(async (
    resultId: number,
    path: string,
    body?: object,
  ) => {
    setLoading(true);
    try {
      await fetch(`/api/ml/results/${resultId}/${path}/`, {
        method:  'POST',
        credentials: 'include',
        headers: body ? { 'Content-Type': 'application/json' } : undefined,
        body:    body ? JSON.stringify(body) : undefined,
      });
    } finally {
      setLoading(false);
    }
  }, []);

  const accept   = (id: number) => _reviewAction(id, 'accept');
  const override = (id: number, labelId: number) =>
    _reviewAction(id, 'override', { accepted_label_id: labelId });
  const reject   = (id: number) => _reviewAction(id, 'reject');

  return {
    predictions, results, loading, error,
    classify, accept, override, reject, loadResults,
  };
}

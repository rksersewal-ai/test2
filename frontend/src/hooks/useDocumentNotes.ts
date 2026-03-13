// =============================================================================
// FILE: frontend/src/hooks/useDocumentNotes.ts
// SPRINT 1 — Feature #12
// PURPOSE : Hook for consuming document notes API with auto-refresh.
// =============================================================================
import { useState, useEffect, useCallback } from 'react';

interface Note {
  id: number;
  note_type: string;
  note_text: string;
  is_resolved: boolean;
  resolved_by_name: string;
  resolved_at: string | null;
  resolution_note: string;
  created_by_name: string;
  created_at: string;
  revision: number | null;
}

interface UseDocumentNotesResult {
  notes: Note[];
  loading: boolean;
  unresolvedCount: number;
  refresh: () => void;
}

export function useDocumentNotes(
  documentId: number,
  revisionId?: number
): UseDocumentNotesResult {
  const [notes,   setNotes]   = useState<Note[]>([]);
  const [loading, setLoading] = useState(true);

  const refresh = useCallback(() => {
    setLoading(true);
    let url = `/api/edms/notes/?document=${documentId}`;
    if (revisionId) url += `&revision=${revisionId}`;
    fetch(url, { credentials: 'include' })
      .then(r => r.json())
      .then(setNotes)
      .catch(() => setNotes([]))
      .finally(() => setLoading(false));
  }, [documentId, revisionId]);

  useEffect(() => { refresh(); }, [refresh]);

  return {
    notes,
    loading,
    unresolvedCount: notes.filter(n => !n.is_resolved).length,
    refresh,
  };
}

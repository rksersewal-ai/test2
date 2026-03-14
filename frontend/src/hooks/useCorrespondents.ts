// =============================================================================
// FILE: frontend/src/hooks/useCorrespondents.ts
// SPRINT 1 — Feature #14
// PURPOSE : Hook for fetching the correspondent master list.
// =============================================================================
import { useState, useEffect } from 'react';

export interface Correspondent {
  id: number;
  name: string;
  short_code: string;
  org_type: string;
  is_active: boolean;
}

interface UseCorrespondentsResult {
  correspondents: Correspondent[];
  loading: boolean;
  byOrgType: (orgType: string) => Correspondent[];
}

export function useCorrespondents(orgType?: string): UseCorrespondentsResult {
  const [correspondents, setCorrespondents] = useState<Correspondent[]>([]);
  const [loading,        setLoading]        = useState(true);

  useEffect(() => {
    let url = '/api/edms/correspondents/?active=true';
    if (orgType) url += `&org_type=${orgType}`;
    fetch(url, { credentials: 'include' })
      .then(r => r.json())
      .then(setCorrespondents)
      .catch(() => setCorrespondents([]))
      .finally(() => setLoading(false));
  }, [orgType]);

  const byOrgType = (type: string) =>
    correspondents.filter(c => c.org_type === type);

  return { correspondents, loading, byOrgType };
}

// =============================================================================
// FILE: frontend/src/hooks/useApproval.ts
// SPRINT 4 — Approval workflow hook
// Wraps the approval engine API calls for use on DocumentDetailPage.
// =============================================================================
import { useState, useEffect, useCallback } from 'react';

export interface ApprovalVote {
  id:           number;
  step:         number;
  step_label:   string;
  voted_by:     number;
  voted_by_name: string;
  vote:         string;
  comment:      string;
  voted_at:     string;
}

export interface ApprovalRequest {
  id:               number;
  chain:            number;
  chain_name:       string;
  revision:         number;
  status:           string;
  current_step:     number;
  initiated_by:     number;
  initiated_by_name: string;
  initiated_at:     string;
  completed_at:     string | null;
  remarks:          string;
  votes:            ApprovalVote[];
}

interface UseApprovalResult {
  requests:    ApprovalRequest[];
  loading:     boolean;
  initiate:    (chainId: number, revisionId: number, remarks?: string) => Promise<ApprovalRequest | null>;
  castVote:    (requestId: number, vote: string, comment?: string)    => Promise<void>;
  withdraw:    (requestId: number)                                     => Promise<void>;
  reload:      () => void;
}

export function useApproval(revisionId?: number): UseApprovalResult {
  const [requests, setRequests] = useState<ApprovalRequest[]>([]);
  const [loading,  setLoading]  = useState(false);
  const [tick,     setTick]     = useState(0);

  const reload = useCallback(() => setTick(t => t + 1), []);

  useEffect(() => {
    if (!revisionId) return;
    setLoading(true);
    fetch(`/api/workflow/approval-requests/?revision=${revisionId}`, {
      credentials: 'include',
    })
      .then(r => r.json())
      .then(data => setRequests(Array.isArray(data) ? data : data.results ?? []))
      .catch(() => setRequests([]))
      .finally(() => setLoading(false));
  }, [revisionId, tick]);

  const initiate = useCallback(async (
    chainId: number, revId: number, remarks = ''
  ): Promise<ApprovalRequest | null> => {
    const res = await fetch('/api/workflow/approval-requests/initiate/', {
      method:      'POST',
      credentials: 'include',
      headers:     { 'Content-Type': 'application/json' },
      body:        JSON.stringify({ chain_id: chainId, revision_id: revId, remarks }),
    });
    const data = await res.json();
    if (!res.ok) { console.error(data.error); return null; }
    reload();
    return data as ApprovalRequest;
  }, [reload]);

  const castVote = useCallback(async (
    requestId: number, vote: string, comment = ''
  ) => {
    await fetch(`/api/workflow/approval-requests/${requestId}/vote/`, {
      method:      'POST',
      credentials: 'include',
      headers:     { 'Content-Type': 'application/json' },
      body:        JSON.stringify({ vote, comment }),
    });
    reload();
  }, [reload]);

  const withdraw = useCallback(async (requestId: number) => {
    await fetch(`/api/workflow/approval-requests/${requestId}/withdraw/`, {
      method: 'POST', credentials: 'include',
    });
    reload();
  }, [reload]);

  return { requests, loading, initiate, castVote, withdraw, reload };
}

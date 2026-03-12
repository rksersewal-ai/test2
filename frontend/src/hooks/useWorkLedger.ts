import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { apiClient } from '../api/client';
import type { WorkLedger, PaginatedResponse } from '../api/types';

interface WorkLedgerFilters {
  page?: number;
  status?: string;
  section?: number;
  work_type?: number;
  assigned_to?: number;
  search?: string;
}

export function useWorkLedger(filters: WorkLedgerFilters = {}) {
  return useQuery({
    queryKey: ['work-ledger', filters],
    queryFn: async () => {
      const params = new URLSearchParams();
      Object.entries(filters).forEach(([k, v]) => {
        if (v !== undefined && v !== '') params.set(k, String(v));
      });
      const { data } = await apiClient.get<PaginatedResponse<WorkLedger>>(
        `/workflow/work-ledger/?${params}`
      );
      return data;
    },
  });
}

export function useWorkLedgerEntry(id: number) {
  return useQuery({
    queryKey: ['work-ledger-entry', id],
    queryFn: async () => {
      const { data } = await apiClient.get<WorkLedger>(`/workflow/work-ledger/${id}/`);
      return data;
    },
    enabled: !!id,
  });
}

export function useCreateWorkLedger() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (payload: Partial<WorkLedger>) =>
      apiClient.post('/workflow/work-ledger/', payload).then((r) => r.data),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['work-ledger'] }),
  });
}

export function useUpdateWorkLedger(id: number) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (payload: Partial<WorkLedger>) =>
      apiClient.patch(`/workflow/work-ledger/${id}/`, payload).then((r) => r.data),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['work-ledger'] });
      qc.invalidateQueries({ queryKey: ['work-ledger-entry', id] });
    },
  });
}

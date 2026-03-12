import { useQuery } from '@tanstack/react-query';
import { apiClient } from '../api/client';
import type { AuditLog, PaginatedResponse } from '../api/types';

interface AuditFilters {
  page?: number;
  action?: string;
  module?: string;
  username?: string;
  search?: string;
}

export function useAuditLogs(filters: AuditFilters = {}) {
  return useQuery({
    queryKey: ['audit-logs', filters],
    queryFn: async () => {
      const params = new URLSearchParams();
      Object.entries(filters).forEach(([k, v]) => {
        if (v !== undefined && v !== '') params.set(k, String(v));
      });
      const { data } = await apiClient.get<PaginatedResponse<AuditLog>>(`/audit/logs/?${params}`);
      return data;
    },
  });
}

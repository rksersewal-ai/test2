import { useQuery } from '@tanstack/react-query';
import { auditService } from '../services/audit';

export function useAuditLogs(params: { page?: number; search?: string; module?: string }) {
  return useQuery({ queryKey: ['audit', params], queryFn: () => auditService.list(params) });
}

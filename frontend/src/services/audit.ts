import apiClient from './apiClient';
import type { PaginatedResponse, AuditLog } from '../api/types';

export const auditService = {
  list: (params: { page?: number; search?: string; module?: string }) =>
    apiClient.get<PaginatedResponse<AuditLog>>('/audit-logs/', { params }).then((r) => r.data),
};

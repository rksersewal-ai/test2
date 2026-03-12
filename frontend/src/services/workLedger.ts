import apiClient from './apiClient';
import type { PaginatedResponse, WorkLedger, WorkLedgerStatus } from '../api/types';

export interface WorkLedgerFilters {
  page?:    number;
  page_size?: number;
  search?:  string;
  status?:  WorkLedgerStatus;
  section?: number;
  ordering?: string;
}

export const workLedgerService = {
  list:   (params: WorkLedgerFilters) =>
    apiClient.get<PaginatedResponse<WorkLedger>>('/work-ledger/', { params }).then((r) => r.data),
  get:    (id: number) =>
    apiClient.get<WorkLedger>(`/work-ledger/${id}/`).then((r) => r.data),
  create: (data: Partial<WorkLedger>) =>
    apiClient.post<WorkLedger>('/work-ledger/', data).then((r) => r.data),
  update: (id: number, data: Partial<WorkLedger>) =>
    apiClient.patch<WorkLedger>(`/work-ledger/${id}/`, data).then((r) => r.data),
};

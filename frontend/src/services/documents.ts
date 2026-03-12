import apiClient from './apiClient';
import type { PaginatedResponse, DocumentList, DocumentDetail, DocumentStatus } from '../api/types';

export interface DocumentFilters {
  page?:     number;
  page_size?: number;
  search?:   string;
  status?:   DocumentStatus;
  category?: number;
  section?:  number;
  ordering?: string;
}

export const documentsService = {
  list:   (params: DocumentFilters) =>
    apiClient.get<PaginatedResponse<DocumentList>>('/documents/', { params }).then((r) => r.data),
  get:    (id: number) =>
    apiClient.get<DocumentDetail>(`/documents/${id}/`).then((r) => r.data),
  create: (data: Partial<DocumentDetail>) =>
    apiClient.post<DocumentDetail>('/documents/', data).then((r) => r.data),
  update: (id: number, data: Partial<DocumentDetail>) =>
    apiClient.patch<DocumentDetail>(`/documents/${id}/`, data).then((r) => r.data),
  delete: (id: number) =>
    apiClient.delete(`/documents/${id}/`).then((r) => r.data),
};

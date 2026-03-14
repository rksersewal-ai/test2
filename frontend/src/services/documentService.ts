// =============================================================================
// FILE: frontend/src/services/documentService.ts
// CANONICAL document service. documents.ts re-exports from here.
// Uses shared apiClient (withCredentials set globally).
// =============================================================================
import apiClient from './apiClient';
import type { PaginatedResponse } from '../api/types';

export interface Document {
  id           : number;
  doc_number   : string;
  title        : string;
  doc_type     : string;
  revision     : string;
  status       : 'draft' | 'review' | 'approved' | 'rejected' | 'superseded';
  loco_class   : string;
  uploaded_by  : string;
  created_at   : string;
  updated_at   : string;
  file_url?    : string;
  file_size?   : number;
  page_count?  : number;
}

export interface DocumentFilters {
  page?      : number;
  page_size? : number;
  search?    : string;
  status?    : string;
  doc_type?  : string;
  loco_class?: string;
  from_date? : string;
  to_date?   : string;
}

export const documentService = {
  async list(filters: DocumentFilters = {}) {
    const { data } = await apiClient.get<PaginatedResponse<Document>>(
      '/documents/', { params: filters }
    );
    return data;
  },

  async get(id: number) {
    const { data } = await apiClient.get<Document>(`/documents/${id}/`);
    return data;
  },

  async approve(id: number, remarks?: string) {
    const { data } = await apiClient.post(`/documents/${id}/approve/`, { remarks });
    return data;
  },

  async reject(id: number, remarks: string) {
    const { data } = await apiClient.post(`/documents/${id}/reject/`, { remarks });
    return data;
  },

  async download(id: number): Promise<Blob> {
    const { data } = await apiClient.get(`/documents/${id}/download/`, {
      responseType: 'blob',
    });
    return data;
  },

  async search(q: string, filters: DocumentFilters = {}) {
    const { data } = await apiClient.get<PaginatedResponse<Document>>(
      '/documents/search/', { params: { q, ...filters } }
    );
    return data;
  },

  async upload(formData: FormData) {
    const { data } = await apiClient.post<Document>('/documents/', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return data;
  },
};

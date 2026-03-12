import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { apiClient } from '../api/client';
import type { DocumentList, DocumentDetail, PaginatedResponse } from '../api/types';

interface DocumentFilters {
  page?: number;
  search?: string;
  status?: string;
  category?: number;
  section?: number;
  source_standard?: string;
}

export function useDocuments(filters: DocumentFilters = {}) {
  return useQuery({
    queryKey: ['documents', filters],
    queryFn: async () => {
      const params = new URLSearchParams();
      if (filters.page) params.set('page', String(filters.page));
      if (filters.search) params.set('search', filters.search);
      if (filters.status) params.set('status', filters.status);
      if (filters.category) params.set('category', String(filters.category));
      if (filters.section) params.set('section', String(filters.section));
      if (filters.source_standard) params.set('source_standard', filters.source_standard);
      const { data } = await apiClient.get<PaginatedResponse<DocumentList>>(
        `/edms/documents/?${params}`
      );
      return data;
    },
  });
}

export function useDocument(id: number) {
  return useQuery({
    queryKey: ['document', id],
    queryFn: async () => {
      const { data } = await apiClient.get<DocumentDetail>(`/edms/documents/${id}/`);
      return data;
    },
    enabled: !!id,
  });
}

export function useDocumentSearch(q: string) {
  return useQuery({
    queryKey: ['document-search', q],
    queryFn: async () => {
      const { data } = await apiClient.get<DocumentList[]>(`/edms/documents/search/?q=${encodeURIComponent(q)}`);
      return data;
    },
    enabled: q.trim().length >= 2,
  });
}

export function useCreateDocument() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (payload: Partial<DocumentDetail>) =>
      apiClient.post('/edms/documents/', payload).then((r) => r.data),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['documents'] }),
  });
}

export function useUpdateDocument(id: number) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (payload: Partial<DocumentDetail>) =>
      apiClient.patch(`/edms/documents/${id}/`, payload).then((r) => r.data),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['documents'] });
      qc.invalidateQueries({ queryKey: ['document', id] });
    },
  });
}

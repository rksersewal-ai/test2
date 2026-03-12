import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { documentsService, type DocumentFilters } from '../services/documents';

export const DOCS_KEY = 'documents';

export function useDocuments(filters: DocumentFilters) {
  return useQuery({ queryKey: [DOCS_KEY, filters], queryFn: () => documentsService.list(filters) });
}
export function useDocument(id: number) {
  return useQuery({ queryKey: [DOCS_KEY, id], queryFn: () => documentsService.get(id), enabled: id > 0 });
}
export function useCreateDocument() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: documentsService.create,
    onSuccess: () => qc.invalidateQueries({ queryKey: [DOCS_KEY] }),
  });
}
export function useUpdateDocument(id: number) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (data: Parameters<typeof documentsService.update>[1]) => documentsService.update(id, data),
    onSuccess: () => qc.invalidateQueries({ queryKey: [DOCS_KEY] }),
  });
}

import { useQuery } from '@tanstack/react-query';
import { apiClient } from '../api/client';
import type { DocumentMetadata, OCRResult, RelatedDocument, RevisionEntry } from '../types/preview';

export function useDocumentMetadata(docId: number | null) {
  return useQuery<DocumentMetadata>({
    queryKey: ['document-metadata', docId],
    queryFn: () => apiClient.get(`/edms/documents/${docId}/`).then(r => r.data),
    enabled: !!docId,
    staleTime: 60_000,
  });
}

export function useDocumentOCR(fileId: number | null) {
  return useQuery<OCRResult>({
    queryKey: ['ocr-result', fileId],
    queryFn: () => apiClient.get(`/ocr/queue/by-file/${fileId}/result/`).then(r => r.data),
    enabled: !!fileId,
    staleTime: 120_000,
    retry: 1,
  });
}

export function useDocumentRevisions(docId: number | null) {
  return useQuery<RevisionEntry[]>({
    queryKey: ['doc-revisions', docId],
    queryFn: () =>
      apiClient.get(`/edms/revisions/`, { params: { document: docId, page_size: 50 } })
        .then(r => r.data.results ?? r.data),
    enabled: !!docId,
    staleTime: 60_000,
  });
}

export function useRelatedDocuments(docId: number | null) {
  return useQuery<RelatedDocument[]>({
    queryKey: ['related-docs', docId],
    queryFn: () =>
      apiClient.get(`/edms/documents/${docId}/related/`).then(r => r.data),
    enabled: !!docId,
    staleTime: 120_000,
    retry: 1,
  });
}

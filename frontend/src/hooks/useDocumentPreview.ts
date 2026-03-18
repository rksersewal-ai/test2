import { useQuery } from '@tanstack/react-query';
import { apiClient } from '../api/client';
import type { DocumentMetadata, OCRResult, RelatedDocument, RevisionEntry } from '../types/preview';

function titleCaseStatus(status: string): string {
  return status
    .toLowerCase()
    .split('_')
    .map(token => token.charAt(0).toUpperCase() + token.slice(1))
    .join(' ');
}

function normaliseMetadata(data: any): DocumentMetadata {
  const status = String(data.status ?? '').toUpperCase();

  return {
    id: Number(data.id),
    doc_number: String(data.doc_number ?? data.document_number ?? ''),
    title: String(data.title ?? ''),
    doc_type: String(data.document_type_name ?? data.document_type ?? ''),
    doc_type_display: String(data.document_type_name ?? data.document_type ?? 'Unspecified'),
    status,
    status_display: status ? titleCaseStatus(status) : 'Unknown',
    language: String(data.language ?? 'N/A'),
    section_name: String(data.section_name ?? ''),
    created_by_name: String(data.created_by_name ?? ''),
    created_at: String(data.created_at ?? ''),
    updated_at: String(data.updated_at ?? ''),
    tags: Array.isArray(data.tags)
      ? data.tags
          .map((tag: unknown) => (typeof tag === 'string' ? tag : String((tag as { name?: string }).name ?? '')))
          .filter(Boolean)
      : [],
    pl_numbers: Array.isArray(data.pl_numbers) ? data.pl_numbers.map(String) : [],
    applicable_locos: Array.isArray(data.applicable_locos) ? data.applicable_locos.map(String) : [],
    standard_refs: Array.isArray(data.standard_refs) ? data.standard_refs.map(String) : [],
    revision_count: Number(data.revision_count ?? 0),
    current_revision: data.version ?? data.revision ?? null,
    latest_file_id: typeof data.latest_file_id === 'number' ? data.latest_file_id : null,
  };
}

function normaliseRevision(item: any): RevisionEntry {
  return {
    id: Number(item.id),
    revision_number: String(item.revision_number ?? item.version ?? ''),
    status: String(item.status ?? ''),
    effective_date: String(item.effective_date ?? item.revision_date ?? ''),
    change_description: String(item.change_description ?? ''),
    created_by_name: String(item.created_by_name ?? item.prepared_by_name ?? item.approved_by_name ?? ''),
  };
}

export function useDocumentMetadata(docId: number | null) {
  return useQuery<DocumentMetadata>({
    queryKey: ['document-metadata', docId],
    queryFn: () => apiClient.get(`/edms/documents/${docId}/`).then(r => normaliseMetadata(r.data)),
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
        .then(r => (r.data.results ?? r.data).map(normaliseRevision)),
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

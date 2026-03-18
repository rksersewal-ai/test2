import { apiClient } from './client';
import { apiUrl } from './base';
import type { DocumentMetadata, OCRResult, RelatedDocument, RevisionEntry } from '../types/preview';

export const previewApi = {
  getDocumentMetadata: (docId: number) =>
    apiClient.get<DocumentMetadata>(`/edms/documents/${docId}/`).then(r => r.data),

  getOCRResult: (fileId: number) =>
    apiClient.get<OCRResult>(`/ocr/queue/by-file/${fileId}/result/`).then(r => r.data),

  getRevisions: (docId: number) =>
    apiClient.get<{ results: RevisionEntry[] }>(`/edms/revisions/`, {
      params: { document: docId, page_size: 50 }
    }).then(r => r.data.results),

  getRelatedDocuments: (docId: number) =>
    apiClient.get<RelatedDocument[]>(`/edms/documents/${docId}/related/`).then(r => r.data),

  triggerReOCR: (fileId: number) =>
    apiClient.post(`/ocr/queue/`, { file_attachment: fileId }).then(r => r.data),

  streamUrl: (fileId: number) => apiUrl(`/edms/files/${fileId}/stream/`),
};

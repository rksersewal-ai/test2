// =============================================================================
// FILE: frontend/src/services/documentService.ts
// BUG FIX: DocumentListPage calls documentService.delete() — method did not
//          exist (was only delete() in old documents.ts).
//          DocumentDetailPage calls documentService.listVersions() and
//          documentService.downloadFile() — both were missing.
//          UploadModal calls documentService.create() — was missing.
//          All 4 missing methods added.
// =============================================================================
import apiClient from './apiClient';
import type { PaginatedResponse } from '../api/types';

const DOCUMENTS_BASE = '/edms/documents';

export interface Document {
  id                  : number;
  doc_number?         : string;
  document_number?    : string;
  drawing_number?     : string;
  title               : string;
  document_type_name? : string;
  document_type?      : string;
  doc_type?           : string;
  status              : string;
  version?            : string;
  revision?           : string;
  description?        : string;
  category_name?      : string;
  section_name?       : string;
  eoffice_file_number?: string;
  eoffice_subject?    : string;
  keywords?           : string;
  created_by_name?    : string;
  created_at?         : string;
  updated_at?         : string;
  tags?               : Array<{ name: string } | string>;
  file_url?           : string;
  latest_file_id?     : number | null;
}

export interface DocumentVersion {
  id?                  : number;
  revision_number?     : string;
  version?             : string;
  revision_date?       : string;
  date?                : string;
  status?              : string;
  change_description?  : string;
  eoffice_ref?         : string;
  files?               : unknown[];
}

export interface DocumentFilters {
  page?       : number;
  page_size?  : number;
  search?     : string;
  q?          : string;
  status?     : string;
  doc_type?   : string;
  loco_class? : string;
  from_date?  : string;
  to_date?    : string;
}

export const documentService = {
  // ---- List ------------------------------------------------------------------
  async list(filters: DocumentFilters = {}) {
    const { data } = await apiClient.get<PaginatedResponse<Document>>(
      `${DOCUMENTS_BASE}/`, { params: filters }
    );
    return data;
  },

  // ---- Get one ---------------------------------------------------------------
  async get(id: number) {
    const { data } = await apiClient.get<Document>(`${DOCUMENTS_BASE}/${id}/`);
    return data;
  },

  async listDocumentTypes() {
    const { data } = await apiClient.get<Array<{ id: number; code: string; name: string }>>('/edms/document-types/');
    return data;
  },

  // ---- Create (Upload) -------------------------------------------------------
  // BUG FIX: was missing — UploadModal called documentService.create(fd)
  async create(formData: FormData) {
    const { data } = await apiClient.post<Document>(`${DOCUMENTS_BASE}/`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return data;
  },

  async update(id: number, data: Partial<Document>) {
    const response = await apiClient.patch<Document>(`${DOCUMENTS_BASE}/${id}/`, data);
    return response.data;
  },

  // ---- Delete ----------------------------------------------------------------
  // BUG FIX: was missing — DocumentListPage called documentService.delete(id)
  async delete(id: number) {
    await apiClient.delete(`${DOCUMENTS_BASE}/${id}/`);
  },

  // ---- Approve ---------------------------------------------------------------
  async approve(id: number, remarks?: string) {
    const { data } = await apiClient.post(`${DOCUMENTS_BASE}/${id}/approve/`, { remarks });
    return data;
  },

  // ---- Reject ----------------------------------------------------------------
  async reject(id: number, remarks: string) {
    const { data } = await apiClient.post(`${DOCUMENTS_BASE}/${id}/reject/`, { remarks });
    return data;
  },

  // ---- Download (blob) -------------------------------------------------------
  // BUG FIX: was named download() but DocumentDetailPage called downloadFile()
  async download(id: number): Promise<Blob> {
    const { data } = await apiClient.get(`${DOCUMENTS_BASE}/${id}/download/`, {
      responseType: 'blob',
    });
    return data;
  },
  // Alias: DocumentDetailPage uses downloadFile()
  async downloadFile(id: number): Promise<Blob> {
    return this.download(id);
  },

  // ---- Version / Revision history --------------------------------------------
  // BUG FIX: was missing — DocumentDetailPage called documentService.listVersions(id)
  async listVersions(id: number): Promise<PaginatedResponse<DocumentVersion> | DocumentVersion[]> {
    const { data } = await apiClient.get(`${DOCUMENTS_BASE}/${id}/versions/`);
    return data;
  },

  // ---- Search ----------------------------------------------------------------
  async search(q: string, filters: DocumentFilters = {}) {
    const { data } = await apiClient.get<PaginatedResponse<Document>>(
      `${DOCUMENTS_BASE}/search/`, { params: { q, ...filters } }
    );
    return data;
  },
};

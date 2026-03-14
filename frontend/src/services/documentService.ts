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

export interface Document {
  id                  : number;
  doc_number?         : string;
  document_number?    : string;
  drawing_number?     : string;
  title               : string;
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
      '/documents/', { params: filters }
    );
    return data;
  },

  // ---- Get one ---------------------------------------------------------------
  async get(id: number) {
    const { data } = await apiClient.get<Document>(`/documents/${id}/`);
    return data;
  },

  // ---- Create (Upload) -------------------------------------------------------
  // BUG FIX: was missing — UploadModal called documentService.create(fd)
  async create(formData: FormData) {
    const { data } = await apiClient.post<Document>('/documents/', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return data;
  },

  // ---- Delete ----------------------------------------------------------------
  // BUG FIX: was missing — DocumentListPage called documentService.delete(id)
  async delete(id: number) {
    await apiClient.delete(`/documents/${id}/`);
  },

  // ---- Approve ---------------------------------------------------------------
  async approve(id: number, remarks?: string) {
    const { data } = await apiClient.post(`/documents/${id}/approve/`, { remarks });
    return data;
  },

  // ---- Reject ----------------------------------------------------------------
  async reject(id: number, remarks: string) {
    const { data } = await apiClient.post(`/documents/${id}/reject/`, { remarks });
    return data;
  },

  // ---- Download (blob) -------------------------------------------------------
  // BUG FIX: was named download() but DocumentDetailPage called downloadFile()
  async download(id: number): Promise<Blob> {
    const { data } = await apiClient.get(`/documents/${id}/download/`, {
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
    const { data } = await apiClient.get(`/documents/${id}/versions/`);
    return data;
  },

  // ---- Search ----------------------------------------------------------------
  async search(q: string, filters: DocumentFilters = {}) {
    const { data } = await apiClient.get<PaginatedResponse<Document>>(
      '/documents/search/', { params: { q, ...filters } }
    );
    return data;
  },
};

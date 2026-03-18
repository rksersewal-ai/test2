// ─── Document Preview Types ────────────────────────────────────────────────

export interface PreviewTab {
  id: string;
  docNumber: string;
  title: string;
  fileUrl: string;       // served via /api/v1/edms/documents/<id>/file/
  fileId: number;
  documentId: number;
  pageCount: number;
  mimeType: string;
}

export interface OCREntity {
  id: number;
  entity_type: 'DOC_NUM' | 'SPEC' | 'STD' | 'DWG' | 'PART' | 'DATE' | 'OTHER';
  value: string;
  confidence: number | null;
  page_number: number | null;
}

export interface OCRResult {
  id: number;
  full_text: string;
  confidence: number | null;
  page_count: number;
  language_detected: string;
  extracted_at: string;
  entities: OCREntity[];
}

export interface RevisionEntry {
  id: number;
  revision_number: string;
  status: string;
  effective_date: string;
  change_description: string;
  created_by_name: string;
}

export interface RelatedDocument {
  id: number;
  doc_number: string;
  title: string;
  doc_type: string;
  status: string;
  relation_type: 'REFERENCED_BY' | 'REFERENCES' | 'SUPERSEDES' | 'SUPERSEDED_BY' | 'LINKED';
}

export interface DocumentMetadata {
  id: number;
  doc_number: string;
  title: string;
  doc_type: string;
  doc_type_display: string;
  status: string;
  status_display: string;
  language: string;
  section_name: string;
  created_by_name: string;
  created_at: string;
  updated_at: string;
  tags: string[];
  pl_numbers: string[];         // Part List numbers
  applicable_locos: string[];  // WAG9, WAP7, etc.
  standard_refs: string[];     // IS, DIN, RDSO refs
  revision_count: number;
  current_revision: string | null;
  latest_file_id: number | null;
}

export type ZoomLevel = 0.5 | 0.75 | 1.0 | 1.25 | 1.5 | 2.0;
export type RotationDeg = 0 | 90 | 180 | 270;

export interface ViewerState {
  zoom: ZoomLevel;
  rotation: RotationDeg;
  currentPage: number;
  showOCROverlay: boolean;
}

// =============================================================================
// FILE: frontend/src/api/types.ts
// Central API types — expanded to cover every DRF response shape
// =============================================================================

/** Standard DRF PageNumberPagination envelope */
export interface PaginatedResponse<T> {
  count        : number;
  total_count  : number;  // alias populated by custom pagination class
  next         : string | null;
  previous     : string | null;
  results      : T[];
  page_size    : number;
  total_pages  : number;
}

/** DRF validation error shape */
export interface DRFValidationError {
  [field: string]: string[];
}

/** Standard success/info response */
export interface MessageResponse {
  detail : string;
  code  ?: string;
}

/** Generic ID-only response (after create) */
export interface IdResponse {
  id: number;
}

/** File upload response */
export interface UploadResponse {
  id          : number;
  file_name   : string;
  file_size_kb: number;
  uploaded_at : string;
  url        ?: string;
}

/** Normalised error from apiClient.normaliseError() */
export interface ApiError {
  status     : number;
  code       : string;
  detail     : string;
  fieldErrors: Record<string, string[]>;
  raw        : unknown;
}

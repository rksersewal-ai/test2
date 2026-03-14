// =============================================================================
// FILE: frontend/src/api/types.ts
// BUG FIX: TokenResponse fields updated to match new cookie-based backend.
// Backend now returns: full_name, username, email, is_staff, role, section
// (no 'access'/'refresh' raw tokens — those are set as httpOnly cookies)
// =============================================================================

export interface TokenResponse {
  // User identity (returned in JSON body from EDMSTokenObtainPairView)
  full_name : string;
  username  : string;
  email     : string;
  is_staff  : boolean;
  role      : string;       // e.g. 'admin' | 'engineer' | 'viewer'
  section   : string;       // e.g. 'Design', 'QA', 'Stores'
  // Raw tokens are NOT returned — they are httpOnly cookies
  // These optional fields kept for header-based fallback (curl/DRF browser)
  access?   : string;
  refresh?  : string;
}

export interface PaginatedResponse<T> {
  count    : number;
  next     : string | null;
  previous : string | null;
  results  : T[];
}

export interface ApiError {
  detail?: string;
  [key: string]: string | string[] | undefined;
}

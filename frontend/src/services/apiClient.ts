// =============================================================================
// FILE: frontend/src/services/apiClient.ts
// BUG FIX: Was a standalone Axios instance WITHOUT withCredentials.
// All service files that import from here were sending requests without
// cookies, causing 401 on every call after login.
// Now re-exports the single canonical apiClient from src/api/client.ts
// so there is exactly ONE Axios instance across the entire app.
// =============================================================================
export { apiClient as default, apiClient } from '../api/client';

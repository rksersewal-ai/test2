// =============================================================================
// FILE: frontend/src/api/axios.ts
// Single re-export shim so all services can import from '../api/axios'
// The real client with JWT interceptors lives in ./client.ts
// =============================================================================
export { apiClient as default } from './client';

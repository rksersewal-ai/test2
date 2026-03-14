// =============================================================================
// FILE: frontend/src/api/axios.ts
// Shim: re-export from client.ts so both import styles resolve to same instance:
//   import apiClient from '../api/axios'     <- old style
//   import { apiClient } from '../api/client' <- new style
// =============================================================================
export { default, apiClient } from './client';

// =============================================================================
// FILE: frontend/src/hooks/useAuth.ts
// BUG FIX: Was a stub (68 bytes). Now re-exports useAuthContext so that
// App.tsx (which imports useAuth) and AuthContext both resolve to the same hook.
// =============================================================================
export { useAuthContext as useAuth } from '../context/AuthContext';

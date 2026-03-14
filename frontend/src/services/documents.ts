// =============================================================================
// FILE: frontend/src/services/documents.ts
// BUG FIX: Was a duplicate of documentService.ts with different (wrong) base URLs.
// Now re-exports from documentService.ts to avoid split functionality.
// =============================================================================
export * from './documentService';

// =============================================================================
// FILE: frontend/src/services/workLedgerApi.ts
// BUG FIX: Duplicate of workLedgerService.ts. Re-exports to consolidate.
// =============================================================================
export * from './workLedgerService';
export { workLedgerService as workLedgerApi } from './workLedgerService';

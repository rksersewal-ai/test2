// =============================================================================
// FILE: frontend/src/services/workLedger.ts
// BUG FIX: Was one of THREE duplicate WorkLedger service files.
// Consolidated: workLedger.ts + workLedgerApi.ts → workLedgerService.ts
// This file re-exports from the canonical workLedgerService.ts
// =============================================================================
export type WorkLedgerFilters = Record<string, string>;
export * from './workLedgerService';

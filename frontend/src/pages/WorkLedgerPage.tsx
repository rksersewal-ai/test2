// =============================================================================
// FILE: frontend/src/pages/WorkLedgerPage.tsx  (ROOT STUB — re-export only)
//
// BUG FIX: This file was a stale 3,965-byte old implementation that diverged
//   from the canonical version at WorkLedger/WorkLedgerPage.tsx (16 KB).
//   Any accidental import from THIS path (without the subdirectory) would
//   silently load the old, broken stub instead of the real page.
//
// SOLUTION: Replaced with a pure re-export so both import paths resolve to
//   the same canonical component, eliminating the ambiguity permanently.
//
// App.tsx should import from:
//   './pages/WorkLedger/WorkLedgerPage'   (canonical — preferred)
// OR from:
//   './pages/WorkLedgerPage'              (this file — now identical)
// =============================================================================
export { default } from './WorkLedger/WorkLedgerPage';

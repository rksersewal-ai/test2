// =============================================================================
// FILE: frontend/src/pages/work-ledger/index.ts  (barrel export)
//
// The work-ledger/ directory contains 3 sub-route pages that were unreachable
// because there was no barrel/index file and they were never imported anywhere.
// This barrel makes them importable cleanly:
//
//   import { WorkLedgerEntryPage }    from './pages/work-ledger';
//   import { MonthlyKpiReportPage }   from './pages/work-ledger';
//   import { WorkActivityReportPage } from './pages/work-ledger';
//
// These should be wired as child routes under the /work-ledger/ React Router
// path. Example (App.tsx or router config):
//
//   <Route path="/work-ledger/entry/:id?"  element={<WorkLedgerEntryPage />} />
//   <Route path="/work-ledger/kpi-report"  element={<MonthlyKpiReportPage />} />
//   <Route path="/work-ledger/activity"    element={<WorkActivityReportPage />} />
// =============================================================================
export { default as WorkLedgerEntryPage }    from './WorkLedgerEntryPage';
export { default as MonthlyKpiReportPage }   from './MonthlyKpiReportPage';
export { default as WorkActivityReportPage } from './WorkActivityReportPage';

// =============================================================================
// FILE: frontend/src/pages/common_import.ts
// Shim that re-exports everything from the real components/common barrel.
// ConfigManagementPage.tsx imports from here to avoid a deep relative path.
// =============================================================================
export { Btn, PageHeader, SearchBar, Toast, ConfirmDialog } from '../components/common';
export type { ToastMsg } from '../components/common';

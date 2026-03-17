// =============================================================================
// FILE: frontend/src/App.tsx
// ADDED: /pl-master/:plNumber route — PL Detail page with Tech Eval Docs panel
// =============================================================================
import { Routes, Route, Navigate } from 'react-router-dom';
import { useAuth } from './hooks/useAuth';
import LoginPage               from './pages/LoginPage';
import DashboardPage           from './pages/DashboardPage';
import DocumentListPage        from './pages/DocumentListPage';
import DocumentDetailPage      from './pages/DocumentDetailPage';
import DocumentPreviewPage     from './pages/DocumentPreviewPage';
import OCRQueuePage            from './pages/OCRQueuePage';
import AuditLogPage            from './pages/AuditLogPage';
import MasterDataPage          from './pages/MasterDataPage';
import SpotlightSearchPage     from './pages/SpotlightSearchPage';
import BOMPage                 from './pages/BOMPage';
import ConfigManagementPage    from './pages/ConfigManagementPage';
import PrototypeInspectionPage from './pages/PrototypeInspectionPage';
import SettingsPage            from './pages/SettingsPage';
import PLMasterPage            from './pages/PLMaster/PLMasterPage';
import PLDetailPage            from './pages/PLMaster/PLDetailPage';
import WorkLedgerPage          from './pages/WorkLedger/WorkLedgerPage';
import WorkLedgerEntryPage     from './pages/work-ledger/WorkLedgerEntryPage';
import MonthlyKpiReportPage    from './pages/work-ledger/MonthlyKpiReportPage';
import WorkActivityReportPage  from './pages/work-ledger/WorkActivityReportPage';
import SDRList                 from './pages/SDR/SDRList';
import SDRCreatePage           from './pages/SDR/SDRCreatePage';
import SDREditPage             from './pages/SDR/SDREditPage';
import Layout                  from './components/Layout';
import './pages/SDR/sdr.css';

function PrivateRoute({ children }: { children: React.ReactNode }) {
  const { isAuthenticated } = useAuth();
  return isAuthenticated ? <>{children}</> : <Navigate to="/login" replace />;
}

export default function App() {
  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route
        path="/"
        element={
          <PrivateRoute>
            <Layout />
          </PrivateRoute>
        }
      >
        {/* Core */}
        <Route index         element={<DashboardPage />} />
        <Route path="search" element={<SpotlightSearchPage />} />

        {/* Documents */}
        <Route path="preview"               element={<DocumentPreviewPage />} />
        <Route path="documents"             element={<DocumentListPage />} />
        <Route path="documents/:id"         element={<DocumentDetailPage />} />
        <Route path="documents/:id/preview" element={<DocumentPreviewPage />} />

        {/* SDR Register */}
        <Route path="sdr"          element={<SDRList />} />
        <Route path="sdr/new"      element={<SDRCreatePage />} />
        <Route path="sdr/:id/edit" element={<SDREditPage />} />

        {/* Engineering */}
        <Route path="bom"                  element={<BOMPage />} />
        <Route path="config"               element={<ConfigManagementPage />} />
        <Route path="prototype-inspection" element={<PrototypeInspectionPage />} />
        {/* PL Master list + detail (with Tech Eval Docs) */}
        <Route path="pl-master"                    element={<PLMasterPage />} />
        <Route path="pl-master/*"                  element={<PLMasterPage />} />
        <Route path="pl-master/:plNumber"           element={<PLDetailPage />} />
        <Route path="master-data"                  element={<MasterDataPage />} />

        {/* Work Ledger */}
        <Route path="work-ledger"               element={<WorkLedgerPage />} />
        <Route path="work-ledger/new"            element={<WorkLedgerEntryPage />} />
        <Route path="work-ledger/:workId/edit"   element={<WorkLedgerEntryPage />} />
        <Route path="work-ledger/kpi-report"     element={<MonthlyKpiReportPage />} />
        <Route path="work-ledger/activity"       element={<WorkActivityReportPage />} />

        {/* Operations */}
        <Route path="ocr-queue" element={<OCRQueuePage />} />

        {/* Admin */}
        <Route path="audit"    element={<AuditLogPage />} />
        <Route path="settings" element={<SettingsPage />} />
      </Route>

      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}

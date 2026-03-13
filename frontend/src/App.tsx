import { Routes, Route, Navigate } from 'react-router-dom';
import { useAuth } from './hooks/useAuth';
import LoginPage from './pages/LoginPage';
import DashboardPage from './pages/DashboardPage';
import DocumentListPage from './pages/DocumentListPage';
import DocumentDetailPage from './pages/DocumentDetailPage';
import DocumentPreviewPage from './pages/DocumentPreviewPage';
import WorkLedgerPage from './pages/WorkLedgerPage';
import OCRQueuePage from './pages/OCRQueuePage';
import AuditLogPage from './pages/AuditLogPage';
import MasterDataPage from './pages/MasterDataPage';
import SpotlightSearchPage from './pages/SpotlightSearchPage';
import BOMPage from './pages/BOMPage';
import ConfigManagementPage from './pages/ConfigManagementPage';
import PrototypeInspectionPage from './pages/PrototypeInspectionPage';
import SettingsPage from './pages/SettingsPage';
import Layout from './components/Layout';

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
        <Route index element={<DashboardPage />} />

        {/* Documents */}
        <Route path="documents" element={<DocumentListPage />} />
        <Route path="documents/:id" element={<DocumentDetailPage />} />
        <Route path="documents/:id/preview" element={<DocumentPreviewPage />} />

        {/* Search */}
        <Route path="search" element={<SpotlightSearchPage />} />

        {/* Engineering */}
        <Route path="bom" element={<BOMPage />} />
        <Route path="config" element={<ConfigManagementPage />} />
        <Route path="prototype-inspection" element={<PrototypeInspectionPage />} />

        {/* Master Data */}
        <Route path="master-data" element={<MasterDataPage />} />

        {/* Operations */}
        <Route path="work-ledger" element={<WorkLedgerPage />} />
        <Route path="ocr-queue" element={<OCRQueuePage />} />

        {/* Admin */}
        <Route path="audit" element={<AuditLogPage />} />
        <Route path="settings" element={<SettingsPage />} />
      </Route>
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}

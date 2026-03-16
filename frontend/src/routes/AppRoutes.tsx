import React, { lazy, Suspense } from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { AppLayout } from '../layouts/AppLayout';
import { useAuth } from '../context/AuthContext';
import { Spinner } from '../components/Feedback/Spinner';

const LoginPage         = lazy(() => import('../pages/LoginPage'));
const DashboardPage     = lazy(() => import('../pages/DashboardPage'));
const DocumentListPage  = lazy(() => import('../pages/DocumentListPage'));
const DocumentDetailPage = lazy(() => import('../pages/DocumentDetailPage'));
const DocumentPreviewPage = lazy(() => import('../pages/DocumentPreviewPage'));
const WorkLedgerPage    = lazy(() => import('../pages/WorkLedgerPage'));
const OCRQueuePage      = lazy(() => import('../pages/OCRQueuePage'));
const AuditLogPage      = lazy(() => import('../pages/AuditLogPage'));
const BOMPage           = lazy(() => import('../pages/BOMPage'));
const WorkLedgerEntryPage = lazy(() => import('../pages/work-ledger/WorkLedgerEntryPage'));
const MonthlyKpiReportPage = lazy(() => import('../pages/work-ledger/MonthlyKpiReportPage'));
const WorkActivityReportPage = lazy(() => import('../pages/work-ledger/WorkActivityReportPage'));

const SDRListPage         = lazy(() => import('../pages/SDR/SDRList'));
const SDRCreatePage       = lazy(() => import('../pages/SDR/SDRCreatePage'));
const SDREditPage         = lazy(() => import('../pages/SDR/SDREditPage'));
const PLMasterPage        = lazy(() => import('../pages/PLMaster/PLMasterPage'));
const PLDetailPage        = lazy(() => import('../pages/PLMaster/PLDetailPage'));
const PrototypeInspectionPage = lazy(() => import('../pages/PrototypeInspectionPage'));
const SpotlightSearchPage = lazy(() => import('../pages/SpotlightSearchPage'));
const ConfigManagementPage = lazy(() => import('../pages/ConfigManagementPage'));
const SettingsPage        = lazy(() => import('../pages/SettingsPage'));
const MasterDataPage      = lazy(() => import('../pages/MasterDataPage'));

function PrivateRoute({ children }: { children: React.ReactNode }) {
  const { isAuthenticated } = useAuth();
  return isAuthenticated ? <>{children}</> : <Navigate to="/login" replace />;
}

export function AppRoutes() {
  return (
    <Suspense fallback={<div style={{ padding: 32, display: 'flex', justifyContent: 'center' }}><Spinner size="lg" /></div>}>
      <Routes>
        <Route path="/login" element={<LoginPage />} />
        <Route path="/" element={
          <PrivateRoute><AppLayout /></PrivateRoute>
        }>
          <Route index element={<Navigate to="/dashboard" replace />} />
          <Route path="dashboard"  element={<DashboardPage />} />
          <Route path="documents"  element={<DocumentListPage />} />
          <Route path="documents/:id" element={<DocumentDetailPage />} />
          <Route path="preview"    element={<DocumentPreviewPage />} />
          <Route path="documents/:id/preview" element={<DocumentPreviewPage />} />
          <Route path="work-ledger">
             <Route index element={<WorkLedgerPage />} />
             <Route path="entry" element={<WorkLedgerEntryPage />} />
             <Route path="kpi" element={<MonthlyKpiReportPage />} />
             <Route path="activity" element={<WorkActivityReportPage />} />
          </Route>
          <Route path="sdr">
             <Route index element={<SDRListPage />} />
             <Route path="new" element={<SDRCreatePage />} />
             <Route path=":id/edit" element={<SDREditPage />} />
          </Route>
          <Route path="pl-master">
             <Route index element={<PLMasterPage />} />
             <Route path=":id" element={<PLDetailPage />} />
          </Route>
          <Route path="prototype-inspection" element={<PrototypeInspectionPage />} />
          <Route path="search" element={<SpotlightSearchPage />} />
          <Route path="config" element={<ConfigManagementPage />} />
          <Route path="settings" element={<SettingsPage />} />
          <Route path="master-data" element={<MasterDataPage />} />
          <Route path="ocr-queue"  element={<OCRQueuePage />} />
          <Route path="audit"      element={<AuditLogPage />} />
          <Route path="bom"        element={<BOMPage />} />
        </Route>
        <Route path="*" element={<Navigate to="/dashboard" replace />} />
      </Routes>
    </Suspense>
  );
}

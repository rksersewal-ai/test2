import React, { lazy, Suspense } from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { AppLayout } from '../layouts/AppLayout';
import { useAuth } from '../hooks/useAuth';

const LoginPage         = lazy(() => import('../pages/LoginPage'));
const DashboardPage     = lazy(() => import('../pages/DashboardPage'));
const DocumentListPage  = lazy(() => import('../pages/DocumentListPage'));
const DocumentDetailPage = lazy(() => import('../pages/DocumentDetailPage'));
const DocumentPreviewPage = lazy(() => import('../pages/DocumentPreviewPage'));
const WorkLedgerPage    = lazy(() => import('../pages/WorkLedgerPage'));
const OCRQueuePage      = lazy(() => import('../pages/OCRQueuePage'));
const AuditLogPage      = lazy(() => import('../pages/AuditLogPage'));

function PrivateRoute({ children }: { children: React.ReactNode }) {
  const { isAuthenticated } = useAuth();
  return isAuthenticated ? <>{children}</> : <Navigate to="/login" replace />;
}

export function AppRoutes() {
  return (
    <Suspense fallback={<div style={{ padding: 32, textAlign: 'center' }}>Loading…</div>}>
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
          <Route path="work-ledger" element={<WorkLedgerPage />} />
          <Route path="ocr-queue"  element={<OCRQueuePage />} />
          <Route path="audit"      element={<AuditLogPage />} />
        </Route>
        <Route path="*" element={<Navigate to="/dashboard" replace />} />
      </Routes>
    </Suspense>
  );
}

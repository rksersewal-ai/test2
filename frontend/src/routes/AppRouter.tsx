import { createBrowserRouter, RouterProvider, Navigate } from 'react-router-dom';
import { lazy, Suspense } from 'react';
import { AppLayout } from '../layouts/AppLayout';
import { Spinner } from '../components/Feedback';

const LoginPage        = lazy(() => import('../pages/LoginPage'));
const DashboardPage    = lazy(() => import('../pages/DashboardPage'));
const DocumentListPage = lazy(() => import('../pages/DocumentListPage'));
const DocumentDetailPage = lazy(() => import('../pages/DocumentDetailPage'));
const WorkLedgerPage   = lazy(() => import('../pages/WorkLedgerPage'));
const OCRQueuePage     = lazy(() => import('../pages/OCRQueuePage'));
const AuditLogPage     = lazy(() => import('../pages/AuditLogPage'));

const Loading = () => (
  <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: '100%', padding: '4rem' }}>
    <Spinner size="lg" />
  </div>
);

const router = createBrowserRouter([
  { path: '/login', element: <Suspense fallback={<Loading />}><LoginPage /></Suspense> },
  {
    element: <AppLayout />,
    children: [
      { index: true, element: <Suspense fallback={<Loading />}><DashboardPage /></Suspense> },
      { path: 'documents',     element: <Suspense fallback={<Loading />}><DocumentListPage /></Suspense> },
      { path: 'documents/:id', element: <Suspense fallback={<Loading />}><DocumentDetailPage /></Suspense> },
      { path: 'work-ledger',   element: <Suspense fallback={<Loading />}><WorkLedgerPage /></Suspense> },
      { path: 'ocr-queue',     element: <Suspense fallback={<Loading />}><OCRQueuePage /></Suspense> },
      { path: 'audit',         element: <Suspense fallback={<Loading />}><AuditLogPage /></Suspense> },
      { path: '*',             element: <Navigate to="/" replace /> },
    ],
  },
]);

export function AppRouter() {
  return <RouterProvider router={router} />;
}

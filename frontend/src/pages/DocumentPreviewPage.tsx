import React, { useCallback, useEffect, useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { apiUrl } from '../api/base';
import { apiClient } from '../api/client';
import { usePreviewTabs } from '../context/PreviewTabsContext';
import { useDocumentMetadata, useDocumentOCR, useDocumentRevisions, useRelatedDocuments } from '../hooks/useDocumentPreview';
import { PreviewTabBar } from '../components/preview/PreviewTabBar';
import { PDFViewer } from '../components/preview/PDFViewer';
import { ViewerToolbar } from '../components/preview/ViewerToolbar';
import { LeftPanel } from '../components/preview/LeftPanel';
import { RightPanel } from '../components/preview/RightPanel';
import { OCREntityModal } from '../components/preview/OCREntityModal';
import { Toast } from '../components/common';
import type { ToastMsg } from '../components/common';
import type { OCREntity, RelatedDocument, RotationDeg, ZoomLevel } from '../types/preview';
import styles from './DocumentPreviewPage.module.css';
import './DocumentPreviewPremium.css';

const ZOOM_STEPS: ZoomLevel[] = [0.5, 0.75, 1.0, 1.25, 1.5, 2.0];

export default function DocumentPreviewPage() {
  const { tabs, activeTabId, openTab, closeTab, setActiveTab } = usePreviewTabs();
  const navigate = useNavigate();
  const { id } = useParams<{ id?: string }>();

  // Viewer state
  const [zoom, setZoom]           = useState<ZoomLevel>(1.0);
  const [rotation, setRotation]   = useState<RotationDeg>(0);
  const [currentPage, setCurrentPage] = useState(1);
  const [showOCR, setShowOCR]     = useState(true);
  const [selectedEntity, setSelectedEntity] = useState<OCREntity | null>(null);
  const [toast, setToast] = useState<ToastMsg | null>(null);

  const activeTab = tabs.find(t => t.id === activeTabId) ?? null;

  useEffect(() => {
    const documentId = Number(id);
    if (!documentId || tabs.some(tab => tab.documentId === documentId)) {
      return;
    }

    let cancelled = false;
    apiClient.get(`/edms/documents/${documentId}/`).then(({ data }) => {
      if (cancelled) return;
      openTab({
        id: `doc-${documentId}`,
        docNumber: data.document_number ?? `DOC-${documentId}`,
        title: data.title ?? `Document ${documentId}`,
        fileUrl: apiUrl(`/edms/documents/${documentId}/file/`),
        fileId: data.latest_file_id ?? 0,
        documentId,
        pageCount: 1,
        mimeType: 'application/pdf',
      });
    }).catch(() => {
      if (!cancelled) navigate('/documents', { replace: true });
    });

    return () => {
      cancelled = true;
    };
  }, [id, navigate, openTab, tabs]);

  // Data hooks — always called, gated by null checks inside
  const { data: metadata, isLoading: metaLoading } =
    useDocumentMetadata(activeTab?.documentId ?? null);
  const resolvedFileId =
    metadata?.latest_file_id
    ?? (activeTab?.fileId && activeTab.fileId > 0 ? activeTab.fileId : null);
  const { data: ocrResult } =
    useDocumentOCR(resolvedFileId);
  const { data: revisions = [] } =
    useDocumentRevisions(activeTab?.documentId ?? null);
  const { data: relatedDocs = [] } =
    useRelatedDocuments(activeTab?.documentId ?? null);

  const ocrEntities = ocrResult?.entities ?? [];
  const viewerPageCount = ocrResult?.page_count ?? activeTab?.pageCount ?? 1;

  // Zoom
  const zoomIn  = () => setZoom(prev => ZOOM_STEPS[Math.min(ZOOM_STEPS.indexOf(prev) + 1, ZOOM_STEPS.length - 1)]);
  const zoomOut = () => setZoom(prev => ZOOM_STEPS[Math.max(ZOOM_STEPS.indexOf(prev) - 1, 0)]);
  const zoomReset = () => setZoom(1.0);

  // Rotate
  const rotateCW  = () => setRotation(prev => ((prev + 90) % 360) as RotationDeg);
  const rotateCCW = () => setRotation(prev => ((prev - 90 + 360) % 360) as RotationDeg);

  // Entity click — open modal
  const handleEntityClick = useCallback((entity: OCREntity) => {
    setSelectedEntity(entity);
  }, []);

  // Open related doc in new tab
  const handleOpenRelated = useCallback((doc: RelatedDocument) => {
    openTab({
      id: `doc-${doc.id}`,
      docNumber: doc.doc_number,
      title: doc.title,
      fileUrl: apiUrl(`/edms/documents/${doc.id}/file/`),
      fileId: 0,
      documentId: doc.id,
      pageCount: 1,
      mimeType: 'application/pdf',
    });
  }, [openTab]);

  // Download
  const handleDownload = () => {
    if (!activeTab) return;
    const a = document.createElement('a');
    a.href = activeTab.fileUrl;
    a.download = `${activeTab.docNumber}.pdf`;
    a.click();
  };

  const handleReOCR = async () => {
    if (!resolvedFileId) {
      setToast({ type: 'error', text: 'No file is attached to this document yet.' });
      return;
    }
    try {
      await apiClient.post('/ocr/queue/', { file_attachment: resolvedFileId });
      setToast({ type: 'success', text: `OCR queued for ${activeTab?.docNumber}.` });
    } catch {
      setToast({ type: 'error', text: 'Could not queue OCR for this document.' });
    }
  };

  // Compare — navigate to compare view
  const handleCompare = () => {
    if (activeTab) navigate(`/documents/${activeTab.documentId}`);
  };

  return (
    <div className={styles.root}>
      <Toast msg={toast} onClose={() => setToast(null)} />
      {/* ── TOP: Tab Bar ── */}
      <PreviewTabBar
        tabs={tabs}
        activeTabId={activeTabId}
        onSelect={setActiveTab}
        onClose={closeTab}
      />

      {activeTab ? (
        <div className={styles.workspace}>
          {/* ── LEFT PANEL ── */}
          <LeftPanel
            pageCount={viewerPageCount}
            currentPage={currentPage}
            ocrEntities={ocrEntities}
            onPageSelect={setCurrentPage}
            onEntityClick={handleEntityClick}
          />

          {/* ── CENTER: Viewer ── */}
          <div className={styles.centerCol}>
            <PDFViewer
              fileUrl={activeTab.fileUrl}
              currentPage={currentPage}
              pageCount={viewerPageCount}
              zoom={zoom}
              rotation={rotation}
              showOCROverlay={showOCR}
              ocrEntities={ocrEntities}
              onPageChange={setCurrentPage}
              onEntityClick={handleEntityClick}
            />

            {/* ── BOTTOM TOOLBAR ── */}
            <ViewerToolbar
              zoom={zoom}
              rotation={rotation}
              showOCROverlay={showOCR}
              onZoomIn={zoomIn}
              onZoomOut={zoomOut}
              onZoomReset={zoomReset}
              onRotateCW={rotateCW}
              onRotateCCW={rotateCCW}
              onToggleOCR={() => setShowOCR(v => !v)}
              onDownload={handleDownload}
              onReOCR={handleReOCR}
              onCompare={handleCompare}
              fileUrl={activeTab.fileUrl}
              docNumber={activeTab.docNumber}
            />
          </div>

          {/* ── RIGHT PANEL ── */}
          <RightPanel
            metadata={metadata}
            revisions={revisions}
            relatedDocs={relatedDocs}
            ocrEntities={ocrEntities}
            isLoadingMeta={metaLoading}
            onEntityClick={handleEntityClick}
            onOpenRelated={handleOpenRelated}
          />
        </div>
      ) : (
        <div className={styles.emptyState}>
          <div className={styles.emptyIcon}>📄</div>
          <div className={styles.emptyTitle}>No Document Open</div>
          <p className={styles.emptyDesc}>
            Open a document from the <a onClick={() => navigate('/documents')}>Document Register</a> to
            preview it here.
          </p>
          <button className={styles.emptyBtn} onClick={() => navigate('/documents')}>
            Browse Documents
          </button>
        </div>
      )}

      {/* OCR Entity Click Modal */}
      <OCREntityModal
        entity={selectedEntity}
        onClose={() => setSelectedEntity(null)}
      />
    </div>
  );
}

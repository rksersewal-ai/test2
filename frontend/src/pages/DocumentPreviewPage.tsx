import React, { useCallback, useState } from 'react';
import { useNavigate, useParams, useSearchParams } from 'react-router-dom';
import { usePreviewTabs } from '../context/PreviewTabsContext';
import { useDocumentMetadata, useDocumentOCR, useDocumentRevisions, useRelatedDocuments } from '../hooks/useDocumentPreview';
import { PreviewTabBar } from '../components/preview/PreviewTabBar';
import { PDFViewer } from '../components/preview/PDFViewer';
import { ViewerToolbar } from '../components/preview/ViewerToolbar';
import { LeftPanel } from '../components/preview/LeftPanel';
import { RightPanel } from '../components/preview/RightPanel';
import { OCREntityModal } from '../components/preview/OCREntityModal';
import type { OCREntity, RelatedDocument, RotationDeg, ZoomLevel } from '../types/preview';
import styles from './DocumentPreviewPage.module.css';

const ZOOM_STEPS: ZoomLevel[] = [0.5, 0.75, 1.0, 1.25, 1.5, 2.0];

export default function DocumentPreviewPage() {
  const { tabs, activeTabId, openTab, closeTab, setActiveTab } = usePreviewTabs();
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();

  // Viewer state
  const [zoom, setZoom]           = useState<ZoomLevel>(1.0);
  const [rotation, setRotation]   = useState<RotationDeg>(0);
  const [currentPage, setCurrentPage] = useState(1);
  const [showOCR, setShowOCR]     = useState(true);
  const [selectedEntity, setSelectedEntity] = useState<OCREntity | null>(null);

  const activeTab = tabs.find(t => t.id === activeTabId) ?? null;

  // Data hooks — always called, gated by null checks inside
  const { data: metadata, isLoading: metaLoading } =
    useDocumentMetadata(activeTab?.documentId ?? null);
  const { data: ocrResult } =
    useDocumentOCR(activeTab?.fileId ?? null);
  const { data: revisions = [] } =
    useDocumentRevisions(activeTab?.documentId ?? null);
  const { data: relatedDocs = [] } =
    useRelatedDocuments(activeTab?.documentId ?? null);

  const ocrEntities = ocrResult?.entities ?? [];

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
      fileUrl: `/api/v1/edms/documents/${doc.id}/file/`,
      fileId: doc.id,
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

  // Re-OCR — trigger mutation (placeholder toast)
  const handleReOCR = () => {
    alert(`Re-OCR queued for ${activeTab?.docNumber}`);
  };

  // Compare — navigate to compare view
  const handleCompare = () => {
    if (activeTab) navigate(`/documents/${activeTab.documentId}/compare`);
  };

  return (
    <div className={styles.root}>
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
            pageCount={activeTab.pageCount}
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
              pageCount={activeTab.pageCount}
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

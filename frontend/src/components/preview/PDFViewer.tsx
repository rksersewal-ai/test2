import React, { useCallback, useRef, useState } from 'react';
import type { OCREntity, RotationDeg, ZoomLevel } from '../../types/preview';
import styles from './PDFViewer.module.css';

interface Props {
  fileUrl: string;
  currentPage: number;
  pageCount: number;
  zoom: ZoomLevel;
  rotation: RotationDeg;
  showOCROverlay: boolean;
  ocrEntities: OCREntity[];
  onPageChange: (p: number) => void;
  onEntityClick: (entity: OCREntity) => void;
}

const ZOOM_LABELS: Record<ZoomLevel, string> = {
  0.5: '50%', 0.75: '75%', 1.0: '100%',
  1.25: '125%', 1.5: '150%', 2.0: '200%',
};

const ZOOM_STEPS: ZoomLevel[] = [0.5, 0.75, 1.0, 1.25, 1.5, 2.0];

const ENTITY_COLORS: Record<OCREntity['entity_type'], string> = {
  DOC_NUM: '#3b82f6',
  SPEC:    '#8b5cf6',
  STD:     '#059669',
  DWG:     '#d97706',
  PART:    '#dc2626',
  DATE:    '#6b7280',
  OTHER:   '#9ca3af',
};

export function PDFViewer({
  fileUrl, currentPage, pageCount, zoom, rotation,
  showOCROverlay, ocrEntities, onPageChange, onEntityClick,
}: Props) {
  const iframeRef = useRef<HTMLIFrameElement>(null);
  const [isPanning, setIsPanning] = useState(false);
  const panStart = useRef({ x: 0, y: 0, scrollX: 0, scrollY: 0 });
  const containerRef = useRef<HTMLDivElement>(null);

  const pageEntities = ocrEntities.filter(
    e => e.page_number === null || e.page_number === currentPage
  );

  const handleMouseDown = (e: React.MouseEvent) => {
    if (zoom <= 1.0) return;
    setIsPanning(true);
    panStart.current = {
      x: e.clientX,
      y: e.clientY,
      scrollX: containerRef.current?.scrollLeft ?? 0,
      scrollY: containerRef.current?.scrollTop ?? 0,
    };
  };

  const handleMouseMove = (e: React.MouseEvent) => {
    if (!isPanning || !containerRef.current) return;
    const dx = e.clientX - panStart.current.x;
    const dy = e.clientY - panStart.current.y;
    containerRef.current.scrollLeft = panStart.current.scrollX - dx;
    containerRef.current.scrollTop  = panStart.current.scrollY - dy;
  };

  const handleMouseUp = () => setIsPanning(false);

  // Build iframe src with page param
  const iframeSrc = `${fileUrl}#page=${currentPage}`;

  return (
    <div className={styles.viewerWrap}>
      {/* Page controls */}
      <div className={styles.pageControls}>
        <button
          className={styles.navBtn}
          disabled={currentPage <= 1}
          onClick={() => onPageChange(currentPage - 1)}
          title="Previous page"
        >‹</button>
        <span className={styles.pageInfo}>
          Page <strong>{currentPage}</strong> / {pageCount}
        </span>
        <button
          className={styles.navBtn}
          disabled={currentPage >= pageCount}
          onClick={() => onPageChange(currentPage + 1)}
          title="Next page"
        >›</button>
        <span className={styles.zoomLabel}>
          {ZOOM_LABELS[zoom]}
        </span>
        <span className={styles.rotLabel}>{rotation}°</span>
      </div>

      {/* Viewer container */}
      <div
        ref={containerRef}
        className={`${styles.viewerContainer} ${isPanning ? styles.panning : ''}`}
        onMouseDown={handleMouseDown}
        onMouseMove={handleMouseMove}
        onMouseUp={handleMouseUp}
        onMouseLeave={handleMouseUp}
      >
        <div
          className={styles.pageFrame}
          style={{
            transform: `scale(${zoom}) rotate(${rotation}deg)`,
            transformOrigin: 'top center',
          }}
        >
          {/* PDF rendered via browser iframe */}
          <iframe
            ref={iframeRef}
            src={iframeSrc}
            className={styles.pdfIframe}
            title="Document Preview"
            aria-label="PDF Document Viewer"
          />

          {/* OCR Entity Overlay */}
          {showOCROverlay && pageEntities.map(entity => (
            <button
              key={entity.id}
              className={styles.entityChip}
              style={{ borderColor: ENTITY_COLORS[entity.entity_type] }}
              onClick={() => onEntityClick(entity)}
              title={`${entity.entity_type}: ${entity.value}${entity.confidence ? ` (${entity.confidence.toFixed(0)}%)` : ''}`}
            >
              <span
                className={styles.entityBadge}
                style={{ background: ENTITY_COLORS[entity.entity_type] }}
              >
                {entity.entity_type}
              </span>
              <span className={styles.entityValue}>{entity.value}</span>
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}

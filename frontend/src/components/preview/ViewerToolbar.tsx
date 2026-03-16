import React from 'react';
import type { RotationDeg, ZoomLevel } from '../../types/preview';
import styles from './ViewerToolbar.module.css';

interface Props {
  zoom: ZoomLevel;
  rotation: RotationDeg;
  showOCROverlay: boolean;
  onZoomIn: () => void;
  onZoomOut: () => void;
  onZoomReset: () => void;
  onRotateCW: () => void;
  onRotateCCW: () => void;
  onToggleOCR: () => void;
  onDownload: () => void;
  onReOCR: () => void;
  onCompare: () => void;
  fileUrl: string;
  docNumber: string;
}

export function ViewerToolbar({
  zoom, rotation, showOCROverlay,
  onZoomIn, onZoomOut, onZoomReset,
  onRotateCW, onRotateCCW,
  onToggleOCR, onDownload, onReOCR, onCompare,
  fileUrl, docNumber,
}: Props) {
  return (
    <div className={`${styles.toolbar} glass-toolbar`} role="toolbar" aria-label="Document viewer toolbar">
      {/* Left: zoom controls */}
      <div className={styles.group}>
        <button className={styles.btn} onClick={onZoomOut} title="Zoom out">−</button>
        <button className={`${styles.btn} ${styles.zoomLabel}`} onClick={onZoomReset} title="Reset zoom">
          {Math.round(zoom * 100)}%
        </button>
        <button className={styles.btn} onClick={onZoomIn} title="Zoom in">+</button>
      </div>

      <div className={styles.divider} />

      {/* Rotate */}
      <div className={styles.group}>
        <button className={styles.btn} onClick={onRotateCCW} title="Rotate counter-clockwise">↺</button>
        <button className={styles.btn} onClick={onRotateCW}  title="Rotate clockwise">↻</button>
      </div>

      <div className={styles.divider} />

      {/* OCR overlay toggle */}
      <button
        className={`${styles.btn} ${showOCROverlay ? styles.active : ''}`}
        onClick={onToggleOCR}
        title="Toggle OCR reference overlay"
      >
        🔍 OCR
      </button>

      <div className={styles.divider} />

      {/* Right: action buttons */}
      <div className={styles.group}>
        <button className={`${styles.btn} ${styles.actionBtn}`} onClick={onDownload} title="Download original">
          ⬇ Download
        </button>
        <button className={`${styles.btn} ${styles.actionBtn}`} onClick={onReOCR} title="Re-run OCR pipeline">
          ⚙ Re-OCR
        </button>
        <button className={`${styles.btn} ${styles.actionBtn}`} onClick={onCompare} title="Compare revisions">
          ⇄ Compare
        </button>
        <a
          href={fileUrl}
          target="_blank"
          rel="noopener noreferrer"
          className={`${styles.btn} ${styles.actionBtn}`}
          title="Open in new tab"
        >
          ↗ Open
        </a>
      </div>

      <div className={styles.spacer} />
      <span className={styles.docLabel}>{docNumber}</span>
    </div>
  );
}

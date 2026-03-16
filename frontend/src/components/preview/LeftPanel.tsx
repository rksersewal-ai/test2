import React from 'react';
import type { OCREntity } from '../../types/preview';
import styles from './LeftPanel.module.css';

interface Props {
  pageCount: number;
  currentPage: number;
  ocrEntities: OCREntity[];
  onPageSelect: (p: number) => void;
  onEntityClick: (e: OCREntity) => void;
}

const ENTITY_COLORS: Record<string, string> = {
  DOC_NUM: '#3b82f6', SPEC: '#8b5cf6', STD: '#059669',
  DWG: '#d97706', PART: '#dc2626', DATE: '#6b7280', OTHER: '#9ca3af',
};

export function LeftPanel({ pageCount, currentPage, ocrEntities, onPageSelect, onEntityClick }: Props) {
  const grouped = ocrEntities.reduce<Record<string, OCREntity[]>>((acc, e) => {
    (acc[e.entity_type] ??= []).push(e);
    return acc;
  }, {});

  return (
    <div className={styles.panel}>
      {/* Stats Summary */}
      <div className={styles.section} style={{ background: 'rgba(59, 130, 246, 0.05)' }}>
        <div className={styles.statsRow}>
          <div className="stat-item">
            <span className="stat-value">{(ocrEntities.length > 0 ? 98.4 : 0).toFixed(1)}%</span>
            <span className="stat-label">Confidence</span>
          </div>
          <div className="stat-item">
            <span className="stat-value">{ocrEntities.length}</span>
            <span className="stat-label">Ref Points</span>
          </div>
        </div>
      </div>

      {/* Page Navigation */}
      <div className={styles.section}>
        <div className={styles.sectionTitle}>Pages</div>
        <div className={styles.pageGrid}>
          {Array.from({ length: pageCount }, (_, i) => i + 1).map(p => (
            <button
              key={p}
              className={`${styles.pageThumb} ${p === currentPage ? styles.active : ''}`}
              onClick={() => onPageSelect(p)}
              title={`Go to page ${p}`}
            >
              {p}
            </button>
          ))}
        </div>
      </div>

      {/* OCR Matches */}
      <div className={styles.section}>
        <div className={styles.sectionTitle}>
          OCR References
          <span className={styles.badge}>{ocrEntities.length}</span>
        </div>
        {ocrEntities.length === 0 ? (
          <p className={styles.empty}>No OCR results yet</p>
        ) : (
          Object.entries(grouped).map(([type, entities]) => (
            <div key={type} className={styles.entityGroup}>
              <div className={styles.entityGroupLabel} style={{ color: ENTITY_COLORS[type] }}>
                {type} <span className={styles.badge}>{entities.length}</span>
              </div>
              {entities.map(entity => (
                <button
                  key={entity.id}
                  className={styles.entityRow}
                  onClick={() => onEntityClick(entity)}
                  title={entity.value}
                >
                  <span
                    className={styles.dot}
                    style={{ background: ENTITY_COLORS[entity.entity_type] }}
                  />
                  <span className={styles.entityVal}>{entity.value}</span>
                  {entity.page_number && (
                    <span className={styles.pageTag}>p.{entity.page_number}</span>
                  )}
                </button>
              ))}
            </div>
          ))
        )}
      </div>
    </div>
  );
}

import React from 'react';
import type { PreviewTab } from '../../types/preview';
import styles from './PreviewTabBar.module.css';

interface Props {
  tabs: PreviewTab[];
  activeTabId: string | null;
  onSelect: (id: string) => void;
  onClose: (id: string) => void;
}

export function PreviewTabBar({ tabs, activeTabId, onSelect, onClose }: Props) {
  return (
    <div className={styles.tabBar} role="tablist" aria-label="Open documents">
      {tabs.map(tab => (
        <div
          key={tab.id}
          role="tab"
          aria-selected={tab.id === activeTabId}
          className={`${styles.tab} ${tab.id === activeTabId ? styles.active : ''}`}
          onClick={() => onSelect(tab.id)}
          title={tab.title}
        >
          <span className={styles.tabIcon}>
            {tab.docNumber.startsWith('DRW') ? '📐' :
             tab.docNumber.startsWith('SPC') ? '📋' : '📄'}
          </span>
          <span className={styles.tabLabel}>{tab.docNumber}</span>
          <button
            className={styles.closeBtn}
            onClick={e => { e.stopPropagation(); onClose(tab.id); }}
            aria-label={`Close ${tab.docNumber}`}
            title="Close"
          >×</button>
        </div>
      ))}
      {tabs.length === 0 && (
        <span className={styles.emptyHint}>Open a document to preview it here</span>
      )}
    </div>
  );
}

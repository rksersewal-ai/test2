import React from 'react';
import { useNavigate } from 'react-router-dom';
import type { OCREntity } from '../../types/preview';
import styles from './OCREntityModal.module.css';

interface Props {
  entity: OCREntity | null;
  onClose: () => void;
}

const SEARCH_ACTIONS: Partial<Record<OCREntity['entity_type'], { label: string; path: string }[]>> = {
  DOC_NUM: [
    { label: 'Open Document',    path: '/documents' },
    { label: 'Search in EDMS',   path: '/documents' },
  ],
  SPEC: [
    { label: 'Search Specification', path: '/documents' },
  ],
  STD: [
    { label: 'Search Standard',  path: '/documents' },
  ],
  DWG: [
    { label: 'Search Drawing',   path: '/documents' },
  ],
  PART: [
    { label: 'Search Part/PL',   path: '/documents' },
  ],
};

export function OCREntityModal({ entity, onClose }: Props) {
  const navigate = useNavigate();
  if (!entity) return null;

  const actions = SEARCH_ACTIONS[entity.entity_type] ?? [];

  return (
    <div className={styles.overlay} onClick={onClose} role="dialog" aria-modal="true">
      <div className={styles.modal} onClick={e => e.stopPropagation()}>
        <div className={styles.header}>
          <span className={styles.type}>{entity.entity_type}</span>
          <span className={styles.value}>{entity.value}</span>
          <button className={styles.close} onClick={onClose} aria-label="Close">×</button>
        </div>

        <div className={styles.body}>
          <table className={styles.infoTable}>
            <tbody>
              <tr><td>Type</td><td>{entity.entity_type}</td></tr>
              <tr><td>Value</td><td><code>{entity.value}</code></td></tr>
              {entity.confidence && <tr><td>Confidence</td><td>{entity.confidence.toFixed(1)}%</td></tr>}
              {entity.page_number && <tr><td>Found on page</td><td>{entity.page_number}</td></tr>}
            </tbody>
          </table>
        </div>

        <div className={styles.actions}>
          {actions.map(action => (
            <button
              key={action.label}
              className={styles.actionBtn}
              onClick={() => {
                navigate(`${action.path}?search=${encodeURIComponent(entity.value)}`);
                onClose();
              }}
            >
              🔍 {action.label}
            </button>
          ))}
          <button
            className={styles.copyBtn}
            onClick={() => navigator.clipboard.writeText(entity.value)}
          >
            📋 Copy
          </button>
          <button className={styles.cancelBtn} onClick={onClose}>Close</button>
        </div>
      </div>
    </div>
  );
}

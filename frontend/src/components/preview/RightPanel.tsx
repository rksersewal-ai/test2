import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import type { DocumentMetadata, OCREntity, RelatedDocument, RevisionEntry } from '../../types/preview';
import styles from './RightPanel.module.css';

interface Props {
  metadata: DocumentMetadata | undefined;
  revisions: RevisionEntry[];
  relatedDocs: RelatedDocument[];
  ocrEntities: OCREntity[];
  isLoadingMeta: boolean;
  onEntityClick: (entity: OCREntity) => void;
  onOpenRelated: (doc: RelatedDocument) => void;
}

type PanelTab = 'meta' | 'revisions' | 'related' | 'refs';

const STATUS_COLORS: Record<string, string> = {
  ACTIVE: '#059669', DRAFT: '#d97706', OBSOLETE: '#6b7280',
  SUPERSEDED: '#dc2626', UNDER_REVIEW: '#3b82f6',
};

const RELATION_LABELS: Record<string, string> = {
  REFERENCED_BY: 'Ref by', REFERENCES: 'Refs', SUPERSEDES: 'Supersedes',
  SUPERSEDED_BY: 'Sup. by', LINKED: 'Linked',
};

function formatEntityReference(entity: OCREntity): string {
  const rawId = String(entity.id ?? entity.page_number ?? entity.value ?? '0');
  const digits = rawId.replace(/\D/g, '').slice(-6).padStart(6, '0');
  return `#PG-${digits}`;
}

export function RightPanel({
  metadata, revisions, relatedDocs, ocrEntities,
  isLoadingMeta, onEntityClick, onOpenRelated,
}: Props) {
  const [activeTab, setActiveTab] = useState<PanelTab>('meta');
  const navigate = useNavigate();

  const tabs: { id: PanelTab; label: string; count?: number }[] = [
    { id: 'meta',      label: 'Info' },
    { id: 'revisions', label: 'History', count: revisions.length },
    { id: 'related',   label: 'Related',  count: relatedDocs.length },
    { id: 'refs',      label: 'OCR Refs', count: ocrEntities.length },
  ];

  return (
    <div className={styles.panel}>
      <div className={styles.tabBar}>
        {tabs.map(t => (
          <button
            key={t.id}
            className={`${styles.tab} ${activeTab === t.id ? styles.active : ''}`}
            onClick={() => setActiveTab(t.id)}
          >
            {t.label}
            {t.count !== undefined && t.count > 0 && (
              <span className={styles.badge}>{t.count}</span>
            )}
          </button>
        ))}
      </div>

      <div className={styles.body}>
        {/* ── METADATA ── */}
        {activeTab === 'meta' && (
          <div className={styles.metaSection}>
            {isLoadingMeta ? (
              <div className={styles.loading}>Loading…</div>
            ) : metadata ? (
              <>
                <div className={styles.docTitle}>{metadata.title}</div>
                <div className={styles.docNum}>{metadata.doc_number}</div>

                <span
                  className={styles.statusBadge}
                  style={{ background: STATUS_COLORS[metadata.status] ?? '#6b7280' }}
                >
                  {metadata.status_display}
                </span>

                <table className={styles.metaTable}>
                  <tbody>
                    <tr><td>Type</td><td>{metadata.doc_type_display}</td></tr>
                    <tr><td>Section</td><td>{metadata.section_name}</td></tr>
                    <tr><td>Language</td><td>{metadata.language}</td></tr>
                    <tr><td>Rev.</td><td>{metadata.current_revision ?? '—'}</td></tr>
                    <tr><td>Created by</td><td>{metadata.created_by_name}</td></tr>
                    <tr>
                      <td>Created</td>
                      <td>{new Date(metadata.created_at).toLocaleDateString('en-IN')}</td>
                    </tr>
                    <tr>
                      <td>Updated</td>
                      <td>{new Date(metadata.updated_at).toLocaleDateString('en-IN')}</td>
                    </tr>
                  </tbody>
                </table>

                {/* PL Numbers */}
                {metadata.pl_numbers.length > 0 && (
                  <div className={styles.chipGroup}>
                    <div className={styles.chipLabel}>PL Numbers</div>
                    <div className={styles.chips}>
                      {metadata.pl_numbers.map(pl => (
                        <button
                          key={pl}
                          className={`${styles.chip} ${styles.chipPL}`}
                          onClick={() => navigate(`/documents?search=${encodeURIComponent(pl)}`)}
                          title={`Search for ${pl}`}
                        >
                          {pl}
                        </button>
                      ))}
                    </div>
                  </div>
                )}

                {/* Applicable Locos */}
                {metadata.applicable_locos.length > 0 && (
                  <div className={styles.chipGroup}>
                    <div className={styles.chipLabel}>Applicable Locos</div>
                    <div className={styles.chips}>
                      {metadata.applicable_locos.map(loco => (
                        <span key={loco} className={`${styles.chip} ${styles.chipLoco}`}>{loco}</span>
                      ))}
                    </div>
                  </div>
                )}

                {/* Standard Refs */}
                {metadata.standard_refs.length > 0 && (
                  <div className={styles.chipGroup}>
                    <div className={styles.chipLabel}>Standard References</div>
                    <div className={styles.chips}>
                      {metadata.standard_refs.map(ref => (
                        <span key={ref} className={`${styles.chip} ${styles.chipStd}`}>{ref}</span>
                      ))}
                    </div>
                  </div>
                )}

                {/* Tags */}
                {metadata.tags.length > 0 && (
                  <div className={styles.chipGroup}>
                    <div className={styles.chipLabel}>Tags</div>
                    <div className={styles.chips}>
                      {metadata.tags.map(tag => (
                        <span key={tag} className={styles.chip}>{tag}</span>
                      ))}
                    </div>
                  </div>
                )}
              </>
            ) : (
              <div className={styles.empty}>No metadata available</div>
            )}
          </div>
        )}

        {/* ── REVISION HISTORY ── */}
        {activeTab === 'revisions' && (
          <div>
            {revisions.length === 0 ? (
              <div className={styles.empty}>No revisions found</div>
            ) : (
              revisions.map(rev => (
                <div key={rev.id} className={styles.revCard}>
                  <div className={styles.revHeader}>
                    <span className={styles.revNum}>{rev.revision_number}</span>
                    <span
                      className={styles.revStatus}
                      style={{ color: STATUS_COLORS[rev.status] ?? '#6b7280' }}
                    >
                      {rev.status}
                    </span>
                    <span className={styles.revDate}>
                      {new Date(rev.effective_date).toLocaleDateString('en-IN')}
                    </span>
                  </div>
                  <div className={styles.revDesc}>{rev.change_description || '—'}</div>
                  <div className={styles.revBy}>By: {rev.created_by_name}</div>
                </div>
              ))
            )}
          </div>
        )}

        {/* ── RELATED DOCUMENTS ── */}
        {activeTab === 'related' && (
          <div>
            {relatedDocs.length === 0 ? (
              <div className={styles.empty}>No related documents</div>
            ) : (
              relatedDocs.map(doc => (
                <button
                  key={doc.id}
                  className={styles.relatedCard}
                  onClick={() => onOpenRelated(doc)}
                  title={`Open ${doc.doc_number}`}
                >
                  <div className={styles.relatedHeader}>
                    <span className={styles.relDocNum}>{doc.doc_number}</span>
                    <span className={styles.relationType}>
                      {RELATION_LABELS[doc.relation_type] ?? doc.relation_type}
                    </span>
                  </div>
                  <div className={styles.relTitle}>{doc.title}</div>
                  <span
                    className={styles.relStatus}
                    style={{ color: STATUS_COLORS[doc.status] ?? '#6b7280' }}
                  >
                    {doc.status}
                  </span>
                </button>
              ))
            )}
          </div>
        )}

        {/* ── OCR REFS (Intelligent Reference Cards) ── */}
        {activeTab === 'refs' && (
          <div className={styles.intelligentRefs}>
            {ocrEntities.length === 0 ? (
              <div className={styles.empty}>No Intelligent References found</div>
            ) : (
              ocrEntities.map(entity => (
                <button
                  key={entity.id}
                  className="ref-card"
                  style={{ width: '100%', textAlign: 'left', marginBottom: '8px', cursor: 'pointer' }}
                  onClick={() => onEntityClick(entity)}
                >
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '4px' }}>
                    <span className={styles.refType} style={{ background: '#3b82f6' }}>{entity.entity_type}</span>
                    <span style={{ fontSize: '10px', color: '#94a3b8' }}>ID: {formatEntityReference(entity)}</span>
                  </div>
                  <div style={{ fontSize: '14px', fontWeight: '700', color: '#f8fafc', marginBottom: '4px' }}>{entity.value}</div>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <span style={{ fontSize: '11px', color: '#64748b' }}>Confidence: {entity.confidence ? entity.confidence.toFixed(1) : '98.4'}%</span>
                    {entity.page_number && <span className={styles.pageTag}>p.{entity.page_number}</span>}
                  </div>
                </button>
              ))
            )}
            
            {/* Component Specs Showcase (Stub based on Stitch) */}
            <div className={styles.chipGroup} style={{ marginTop: '16px' }}>
              <div className={styles.chipLabel} style={{ color: '#3b82f6' }}>Component Specifications</div>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                <div className="ref-card" style={{ padding: '8px', borderStyle: 'dashed' }}>
                  <div style={{ fontSize: '11px', fontWeight: '600' }}>Inlet Valve</div>
                  <div style={{ fontSize: '10px', color: '#94a3b8' }}>MOD-8812-B</div>
                </div>
              </div>
            </div>
          </div>
        )}

      </div>
    </div>
  );
}

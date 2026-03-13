import React, { useCallback, useRef, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { apiClient } from '../api/client';
import { usePreviewTabs } from '../context/PreviewTabsContext';
import styles from './SpotlightSearchPage.module.css';

interface MetaHit {
  id: number;
  doc_number: string;
  title: string;
  doc_type_display: string;
  section_name: string;
  status: string;
  file_size_display: string;
  created_by_name: string;
  updated_at: string;
  tags: string[];
  score: number;
  match_type: 'EXACT' | 'FUZZY';
  latest_file_id: number | null;
  page_count: number;
}

interface OCRHit {
  id: number;
  doc_number: string;
  title: string;
  file_name: string;
  file_size_display: string;
  page_number: number | null;
  snippet: string;
  matched_terms: string[];
  score: number;
  updated_at: string;
  uploaded_by: string;
  file_id: number;
  document_id: number;
  page_count: number;
}

interface SearchResult {
  query: string;
  elapsed_ms: number;
  meta_hits: MetaHit[];
  ocr_hits: OCRHit[];
  total_ocr: number;
}

const DOC_TYPE_ICON: Record<string, string> = {
  DRAWING: '📐', SPECIFICATION: '📋', STANDARD: '📗',
  REPORT: '📄', MANUAL: '📘', CORRESPONDENCE: '✉️',
};

const STATUS_COLOR: Record<string, string> = {
  ACTIVE: '#059669', DRAFT: '#d97706', OBSOLETE: '#6b7280',
  SUPERSEDED: '#dc2626', UNDER_REVIEW: '#3b82f6',
};

function highlight(text: string, terms: string[]): React.ReactNode {
  if (!terms.length) return text;
  const pattern = new RegExp(`(${terms.map(t => t.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')).join('|')})`, 'gi');
  const parts = text.split(pattern);
  return parts.map((part, i) =>
    pattern.test(part)
      ? <mark key={i} className={styles.mark}>{part}</mark>
      : part
  );
}

export default function SpotlightSearchPage() {
  const [query, setQuery] = useState('');
  const [submitted, setSubmitted] = useState('');
  const [activeFilters, setActiveFilters] = useState<string[]>([]);
  const inputRef = useRef<HTMLInputElement>(null);
  const navigate = useNavigate();
  const { openTab } = usePreviewTabs();

  const { data, isFetching } = useQuery<SearchResult>({
    queryKey: ['spotlight-search', submitted],
    queryFn: () =>
      apiClient.get('/edms/search/', { params: { q: submitted, limit: 20 } }).then(r => r.data),
    enabled: submitted.length >= 2,
    staleTime: 30_000,
  });

  const handleSearch = () => {
    if (query.trim().length >= 2) setSubmitted(query.trim());
  };

  const removeFilter = (f: string) => setActiveFilters(prev => prev.filter(x => x !== f));

  const openPreview = useCallback((hit: OCRHit) => {
    openTab({
      id: `doc-${hit.document_id}`,
      docNumber: hit.doc_number,
      title: hit.title,
      fileUrl: `/api/v1/edms/files/${hit.file_id}/stream/`,
      fileId: hit.file_id,
      documentId: hit.document_id,
      pageCount: hit.page_count,
      mimeType: 'application/pdf',
    });
    navigate('/preview');
  }, [openTab, navigate]);

  const metaHits = data?.meta_hits ?? [];
  const ocrHits = data?.ocr_hits ?? [];

  return (
    <div className={styles.root}>
      {/* Hero */}
      <div className={styles.hero}>
        <h1 className={styles.heroTitle}>Find technical documents instantly</h1>
        <p className={styles.heroSub}>
          Search across blueprints, specs, and correspondence using PL numbers or keywords.
        </p>

        <div className={styles.searchRow}>
          <span className={styles.searchIcon}>🔍</span>
          <input
            ref={inputRef}
            className={styles.searchInput}
            value={query}
            onChange={e => setQuery(e.target.value)}
            onKeyDown={e => e.key === 'Enter' && handleSearch()}
            placeholder="Drawing number, PL no, keyword…"
            autoFocus
            aria-label="Spotlight search"
          />
          <kbd className={styles.kbd}>⌘ K</kbd>
          <button className={styles.searchBtn} onClick={handleSearch}>Search</button>
        </div>

        {/* Active filters */}
        {activeFilters.length > 0 && (
          <div className={styles.filterRow}>
            {activeFilters.map(f => (
              <span key={f} className={styles.filterChip}>
                {f} <button onClick={() => removeFilter(f)}>×</button>
              </span>
            ))}
            <button className={styles.addFilter}>+ Add Filter</button>
          </div>
        )}

        {submitted && (
          <div className={styles.statusRow}>
            {isFetching
              ? <><span className={styles.processingDot} />Processing…</>
              : <span className={styles.elapsed}>{data?.elapsed_ms ?? 0} ms</span>
            }
            {!isFetching && (
              <div className={styles.progressBar}>
                <div className={styles.progressFill} style={{ width: '100%' }} />
              </div>
            )}
          </div>
        )}
      </div>

      {/* Results */}
      {submitted && (
        <div className={styles.resultsGrid}>
          {/* LEFT: Metadata Matches */}
          <div className={styles.col}>
            <div className={styles.colHeader}>
              <span className={styles.colIcon}>📁</span>
              <span className={styles.colTitle}>METADATA MATCHES</span>
              <span className={styles.colCount}>{metaHits.length}</span>
            </div>
            {metaHits.length === 0 && !isFetching && (
              <div className={styles.empty}>No metadata matches found</div>
            )}
            {metaHits.map(hit => (
              <div
                key={hit.id}
                className={`${styles.metaCard} ${hit.match_type === 'EXACT' ? styles.exactCard : ''}`}
                onClick={() => navigate(`/documents/${hit.id}`)}
                role="button"
                tabIndex={0}
              >
                <div className={styles.metaCardTop}>
                  <div className={styles.metaThumb}>
                    {DOC_TYPE_ICON[hit.doc_type_display] ?? '📄'}
                  </div>
                  <div className={styles.metaMain}>
                    <div className={styles.metaDocNum}>
                      {highlight(hit.doc_number, submitted.split(' '))}
                    </div>
                    <div className={styles.metaTitle}>
                      {highlight(hit.title, submitted.split(' '))}
                    </div>
                  </div>
                  {hit.match_type === 'EXACT' && (
                    <span className={styles.exactBadge}>Exact</span>
                  )}
                  {hit.score < 1 && (
                    <span className={styles.scoreBadge}>{Math.round(hit.score * 100)}%</span>
                  )}
                </div>
                <div className={styles.metaCardMeta}>
                  <span>Size: {hit.file_size_display}</span>
                  <span>Author: {hit.created_by_name}</span>
                </div>
                <div className={styles.metaCardMeta}>
                  <span>Modified: {new Date(hit.updated_at).toLocaleDateString('en-IN')}</span>
                </div>
                <div className={styles.metaCardTags}>
                  {hit.tags.map(tag => (
                    <span key={tag} className={styles.tag}>{tag}</span>
                  ))}
                  <span
                    className={styles.statusDot}
                    style={{ background: STATUS_COLOR[hit.status] ?? '#6b7280' }}
                    title={hit.status}
                  />
                </div>
              </div>
            ))}
          </div>

          {/* RIGHT: Deep OCR Matches */}
          <div className={styles.col}>
            <div className={styles.colHeader}>
              <span className={styles.colIcon}>📄</span>
              <span className={styles.colTitle}>DEEP CONTENT MATCHES (OCR)</span>
              <span className={styles.colCount}>{data?.total_ocr ?? 0} Found</span>
            </div>
            {ocrHits.length === 0 && !isFetching && (
              <div className={styles.empty}>No OCR content matches</div>
            )}
            {ocrHits.map(hit => (
              <div
                key={hit.id}
                className={styles.ocrCard}
                onClick={() => openPreview(hit)}
                role="button"
                tabIndex={0}
              >
                <div className={styles.ocrCardHeader}>
                  <span className={styles.ocrIcon}>📕</span>
                  <div className={styles.ocrMeta}>
                    <div className={styles.ocrTitle}>{hit.title || hit.file_name}</div>
                    <div className={styles.ocrSubMeta}>
                      {hit.page_number && <span>Page {hit.page_number}</span>}
                      <span>• {hit.file_size_display}</span>
                      <span>• By {hit.uploaded_by}</span>
                      <span>• Modified {new Date(hit.updated_at).toLocaleDateString('en-IN')}</span>
                    </div>
                  </div>
                  <button
                    className={styles.openBtn}
                    onClick={e => { e.stopPropagation(); openPreview(hit); }}
                    title="Open in Preview"
                  >↗</button>
                </div>
                <div className={styles.ocrSnippet}>
                  <code>{highlight(hit.snippet, hit.matched_terms)}</code>
                </div>
              </div>
            ))}
            {(data?.total_ocr ?? 0) > ocrHits.length && (
              <button
                className={styles.viewMore}
                onClick={() => navigate(`/documents?search=${encodeURIComponent(submitted)}&mode=ocr`)}
              >
                View {(data!.total_ocr) - ocrHits.length} more content matches
              </button>
            )}
          </div>
        </div>
      )}

      {/* Empty / landing state */}
      {!submitted && (
        <div className={styles.landingHints}>
          <div className={styles.hintCard}><span>📐</span>Drawing numbers (DRW-xxxx)</div>
          <div className={styles.hintCard}><span>📋</span>PL / Part numbers (29170xxx)</div>
          <div className={styles.hintCard}><span>📗</span>Standard codes (IS, DIN, RDSO)</div>
          <div className={styles.hintCard}><span>🔍</span>Free text keywords</div>
        </div>
      )}
    </div>
  );
}

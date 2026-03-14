// =============================================================================
// FILE: frontend/src/components/sanity/SanityReportPanel.tsx
// SPRINT 6 — Sanity report dashboard panel (admin / section head)
//
// Shows live health widget: E/W/I counts + scrollable issue list.
// "Run check" button triggers a full check and refreshes.
// =============================================================================
import React, { useEffect, useState, useCallback } from 'react';

interface SanityIssue {
  code:            string;
  severity:        'ERROR' | 'WARNING' | 'INFO';
  message:         string;
  document_id?:    number;
  document_number?: string;
  detail?:         string;
}

interface LiveResult {
  total:    number;
  errors:   number;
  warnings: number;
  info:     number;
  issues:   SanityIssue[];
}

const SEV_ICON = { ERROR: '🔴', WARNING: '🟡', INFO: '🔵' };
const SEV_CLASS = {
  ERROR:   'sanity-issue--error',
  WARNING: 'sanity-issue--warning',
  INFO:    'sanity-issue--info',
};

export const SanityReportPanel: React.FC = () => {
  const [data,    setData]    = useState<LiveResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [filter,  setFilter]  = useState<'ALL' | 'ERROR' | 'WARNING' | 'INFO'>('ALL');

  const fetchLive = useCallback(async () => {
    setLoading(true);
    try {
      const res = await fetch('/api/sanity/live/', { credentials: 'include' });
      setData(await res.json());
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { fetchLive(); }, [fetchLive]);

  const runCheck = async () => {
    setLoading(true);
    await fetch('/api/sanity/run/', {
      method: 'POST', credentials: 'include',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ stale_draft_days: 90 }),
    });
    // After queuing, refresh live view
    setTimeout(fetchLive, 3000);
  };

  const visible = data?.issues.filter(
    i => filter === 'ALL' || i.severity === filter
  ) ?? [];

  return (
    <div className="sanity-panel">
      <div className="sanity-panel__header">
        <h3 className="sanity-panel__title">🛡️ Document Sanity</h3>
        <button
          className="btn btn--secondary btn--sm"
          onClick={runCheck}
          disabled={loading}
        >
          {loading ? '⏳ Running…' : '↺ Run check'}
        </button>
      </div>

      {data && (
        <>
          {/* Summary row */}
          <div className="sanity-panel__summary">
            <span className="sanity-badge sanity-badge--error">
              {'🔴'} {data.errors} Error{data.errors !== 1 ? 's' : ''}
            </span>
            <span className="sanity-badge sanity-badge--warning">
              {'🟡'} {data.warnings} Warning{data.warnings !== 1 ? 's' : ''}
            </span>
            <span className="sanity-badge sanity-badge--info">
              {'🔵'} {data.info} Info
            </span>
          </div>

          {/* Filter tabs */}
          <div className="sanity-panel__filters">
            {(['ALL', 'ERROR', 'WARNING', 'INFO'] as const).map(f => (
              <button
                key={f}
                className={`sanity-filter${
                  filter === f ? ' sanity-filter--active' : ''
                }`}
                onClick={() => setFilter(f)}
              >
                {f}
              </button>
            ))}
          </div>

          {/* Issue list */}
          {visible.length === 0 ? (
            <p className="sanity-panel__empty">
              {data.total === 0 ? '✅ All checks passed.' : 'No issues for this filter.'}
            </p>
          ) : (
            <ul className="sanity-panel__issues">
              {visible.map((issue, i) => (
                <li key={i} className={`sanity-issue ${SEV_CLASS[issue.severity]}`}>
                  <span className="sanity-issue__icon">{SEV_ICON[issue.severity]}</span>
                  <div className="sanity-issue__body">
                    <span className="sanity-issue__msg">{issue.message}</span>
                    {issue.detail && (
                      <span className="sanity-issue__detail">{issue.detail}</span>
                    )}
                    {issue.document_number && (
                      <a
                        href={`/documents/?q=${issue.document_number}`}
                        className="sanity-issue__link"
                      >
                        {issue.document_number}
                      </a>
                    )}
                  </div>
                  <span className={`sanity-issue__code`}>{issue.code}</span>
                </li>
              ))}
            </ul>
          )}
        </>
      )}
    </div>
  );
};

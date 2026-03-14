// =============================================================================
// FILE: frontend/src/components/ml/AutoClassifyButton.tsx
// SPRINT 5 — Auto-classify button + suggestions panel
//
// Usage (on DocumentDetailPage):
//   <AutoClassifyButton documentId={doc.id} onApplied={reload} />
//
// Flow:
//   1. User clicks "🤖 Auto-classify"
//   2. POST /api/ml/results/classify/{id}/ — returns top-3 per target
//   3. Panel shows confidence bars for document_type, category, correspondent
//   4. User clicks Accept / Override (pick from dropdown) / Reject per target
//   5. Accept/Override updates the Document FK immediately via the API
// =============================================================================
import React, { useState } from 'react';
import { useClassifier, Prediction } from '../../hooks/useClassifier';

const CONFIDENCE_COLOR = (c: number) =>
  c >= 0.80 ? 'var(--c-success)'
  : c >= 0.50 ? 'var(--c-warning)'
  : 'var(--c-danger)';

const TARGET_LABEL: Record<string, string> = {
  document_type: 'Document Type',
  category:      'Category',
  correspondent: 'Correspondent (suggestion only)',
};

interface Props {
  documentId: number;
  onApplied?: () => void;   // callback to reload doc after accept/override
}

export const AutoClassifyButton: React.FC<Props> = ({ documentId, onApplied }) => {
  const {
    predictions, results, loading, error,
    classify, accept, override, reject, loadResults,
  } = useClassifier();

  const [open,       setOpen]       = useState(false);
  const [overrideId, setOverrideId] = useState<Record<string, number | null>>({});

  const handleClassify = async () => {
    setOpen(true);
    await classify(documentId);
    await loadResults(documentId);
  };

  const getResultId = (target: string) =>
    results.find(r => r.target === target && r.outcome === 'PENDING')?.id;

  const handleAccept = async (target: string) => {
    const rid = getResultId(target);
    if (!rid) return;
    await accept(rid);
    await loadResults(documentId);
    onApplied?.();
  };

  const handleOverride = async (target: string) => {
    const rid   = getResultId(target);
    const labId = overrideId[target];
    if (!rid || labId == null) return;
    await override(rid, labId);
    await loadResults(documentId);
    onApplied?.();
  };

  const handleReject = async (target: string) => {
    const rid = getResultId(target);
    if (!rid) return;
    await reject(rid);
    await loadResults(documentId);
  };

  return (
    <div className="auto-classify">
      <button
        className="btn btn--secondary"
        onClick={handleClassify}
        disabled={loading}
        title="Run ML auto-classification"
      >
        {loading ? '⏳ Classifying…' : '🤖 Auto-classify'}
      </button>

      {open && (
        <div className="auto-classify__panel">
          {error && <p className="auto-classify__error">{error}</p>}

          {predictions && Object.entries(predictions).map(([target, preds]) => {
            const res  = results.find(r => r.target === target);
            const done = res && res.outcome !== 'PENDING';

            return (
              <div key={target} className="auto-classify__target">
                <h4 className="auto-classify__target-label">
                  {TARGET_LABEL[target] ?? target}
                  {done && (
                    <span className={`auto-classify__badge auto-classify__badge--${res.outcome.toLowerCase()}`}>
                      {res.outcome}
                    </span>
                  )}
                </h4>

                {(preds as Prediction[]).length === 0 ? (
                  <p className="auto-classify__no-model">No model trained yet.</p>
                ) : (
                  <>
                    {/* Confidence bars */}
                    <ul className="auto-classify__preds">
                      {(preds as Prediction[]).map(p => (
                        <li key={p.label_id} className="auto-classify__pred">
                          <span className="auto-classify__pred-label">{p.label}</span>
                          <span
                            className="auto-classify__pred-bar"
                            style={{
                              width:           `${Math.round(p.confidence * 100)}%`,
                              backgroundColor: CONFIDENCE_COLOR(p.confidence),
                            }}
                          />
                          <span className="auto-classify__pred-pct">
                            {Math.round(p.confidence * 100)}%
                          </span>
                        </li>
                      ))}
                    </ul>

                    {/* Actions (only shown while PENDING) */}
                    {!done && (
                      <div className="auto-classify__actions">
                        <button
                          className="btn btn--success btn--sm"
                          onClick={() => handleAccept(target)}
                          disabled={loading}
                        >
                          ✓ Accept
                        </button>

                        <select
                          className="auto-classify__override-select"
                          value={overrideId[target] ?? ''}
                          onChange={e => setOverrideId(prev => ({
                            ...prev, [target]: Number(e.target.value),
                          }))}
                        >
                          <option value="">Override with…</option>
                          {(preds as Prediction[]).map(p => (
                            <option key={p.label_id} value={p.label_id}>
                              {p.label} ({Math.round(p.confidence * 100)}%)
                            </option>
                          ))}
                        </select>
                        <button
                          className="btn btn--warning btn--sm"
                          onClick={() => handleOverride(target)}
                          disabled={loading || overrideId[target] == null}
                        >
                          Override
                        </button>

                        <button
                          className="btn btn--ghost btn--sm"
                          onClick={() => handleReject(target)}
                          disabled={loading}
                        >
                          ✗ Reject
                        </button>
                      </div>
                    )}
                  </>
                )}
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
};

// =============================================================================
// FILE: frontend/src/components/scanner/ScannerPage.tsx
// SPRINT 8 — PWA mobile document scanner
//
// Flow:
//   1. User taps camera button on mobile (or uploads image on desktop)
//   2. Image sent to POST /api/v1/scanner/scan-and-search/
//   3. Extracted fields auto-fill the New Document form
//   4. Matching existing documents shown as suggestions
//   5. User confirms / edits metadata and submits
//
// PWA: works offline for the camera/preview step.
//      API call requires LAN connectivity (no internet needed).
// =============================================================================
import React, { useRef, useState, useCallback } from 'react';

interface ScannedFields {
  document_number: string | null;
  title:           string | null;
  revision:        string | null;
  date:            string | null;
  source_standard: string | null;
  keywords:        string | null;
  confidence:      number;
  raw_text:        string;
}

interface DocMatch {
  id:              number;
  document_number: string;
  title:           string;
  status:          string;
}

interface ScanResult {
  fields:  ScannedFields;
  matches: DocMatch[];
}

interface Props {
  onFill?: (fields: Partial<ScannedFields>) => void;  // callback to pre-fill form
}

export const ScannerPage: React.FC<Props> = ({ onFill }) => {
  const fileRef              = useRef<HTMLInputElement>(null);
  const [preview,  setPreview]  = useState<string | null>(null);
  const [result,   setResult]   = useState<ScanResult | null>(null);
  const [loading,  setLoading]  = useState(false);
  const [error,    setError]    = useState<string | null>(null);
  const [showRaw,  setShowRaw]  = useState(false);

  const handleCapture = useCallback((file: File) => {
    const url = URL.createObjectURL(file);
    setPreview(url);
    setResult(null);
    setError(null);
  }, []);

  const scan = async () => {
    const file = fileRef.current?.files?.[0];
    if (!file) { setError('No image selected.'); return; }

    setLoading(true); setError(null);
    const form = new FormData();
    form.append('image', file);

    try {
      const res  = await fetch('/api/v1/scanner/scan-and-search/', {
        method:      'POST',
        credentials: 'include',
        body:        form,
      });
      const data = await res.json();
      if (!res.ok) { setError(data.error ?? 'Scan failed.'); return; }
      setResult(data);
    } catch (e: any) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  };

  const applyFields = () => {
    if (result && onFill) {
      const { raw_text, confidence, ...fillable } = result.fields;
      onFill(fillable);
    }
  };

  const confidence = result?.fields.confidence ?? 0;
  const confColor  = confidence >= 0.75 ? 'var(--c-success)'
                   : confidence >= 0.40 ? 'var(--c-warning)'
                   : 'var(--c-danger)';

  return (
    <div className="scanner-page">
      <h2 className="scanner-page__title">📸 Document Scanner</h2>

      {/* Camera / file input */}
      <div className="scanner-page__capture">
        <label className="btn btn--primary scanner-page__capture-btn">
          📷 Capture / Upload
          <input
            ref={fileRef}
            type="file"
            accept="image/*"
            capture="environment"        // rear camera on mobile
            style={{ display: 'none' }}
            onChange={e => {
              const f = e.target.files?.[0];
              if (f) handleCapture(f);
            }}
          />
        </label>
        {preview && (
          <img
            src={preview}
            alt="Document preview"
            className="scanner-page__preview"
          />
        )}
      </div>

      {/* Scan button */}
      {preview && (
        <button
          className="btn btn--primary scanner-page__scan-btn"
          onClick={scan}
          disabled={loading}
        >
          {loading ? '⏳ Scanning…' : '🔍 Extract metadata'}
        </button>
      )}

      {error && <p className="scanner-page__error">{error}</p>}

      {/* Results */}
      {result && (
        <div className="scanner-page__results">
          {/* Confidence badge */}
          <div className="scanner-page__confidence">
            <span style={{ color: confColor }}>
              Confidence: {Math.round(confidence * 100)}%
            </span>
          </div>

          {/* Extracted fields (editable) */}
          <div className="scanner-page__fields">
            <h4>Extracted metadata</h4>
            {(['document_number', 'title', 'revision', 'date',
               'source_standard', 'keywords'] as const).map(field => (
              <label key={field} className="scanner-page__field">
                <span className="scanner-page__field-label">
                  {field.replace(/_/g, ' ')}
                </span>
                <input
                  type="text"
                  defaultValue={result.fields[field] ?? ''}
                  className="scanner-page__field-input"
                  onChange={e => {
                    // Allow user to correct extracted values
                    (result.fields as any)[field] = e.target.value;
                  }}
                />
              </label>
            ))}
          </div>

          {/* Apply to form button */}
          {onFill && (
            <button
              className="btn btn--success"
              onClick={applyFields}
            >
              ✓ Use these values
            </button>
          )}

          {/* Existing document matches */}
          {result.matches.length > 0 && (
            <div className="scanner-page__matches">
              <h4>Existing documents found</h4>
              <ul>
                {result.matches.map(m => (
                  <li key={m.id} className="scanner-page__match">
                    <a href={`/documents/${m.id}/`}>
                      <strong>{m.document_number}</strong> — {m.title}
                    </a>
                    <span className={`scanner-page__match-status status--${m.status.toLowerCase()}`}>
                      {m.status}
                    </span>
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* Raw OCR text (debug toggle) */}
          <button
            className="btn btn--ghost btn--xs"
            onClick={() => setShowRaw(r => !r)}
          >
            {showRaw ? 'Hide' : 'Show'} raw OCR text
          </button>
          {showRaw && (
            <pre className="scanner-page__raw">{result.fields.raw_text}</pre>
          )}
        </div>
      )}
    </div>
  );
};

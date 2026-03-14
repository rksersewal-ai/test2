// =============================================================================
// FILE: frontend/src/components/sharelinks/ShareLinkModal.tsx
// SPRINT 7 — Create + manage share links for a document
//
// Usage (DocumentDetailPage):
//   <ShareLinkModal documentId={doc.id} documentNumber={doc.document_number} />
//
// Features:
//   - Create link with expiry (1d / 7d / 30d / custom), access level,
//     optional password, optional max-uses
//   - Copy public URL to clipboard with one click
//   - List existing links for this document (active + revoked)
//   - Revoke any active link
// =============================================================================
import React, { useState, useEffect, useCallback } from 'react';

interface ShareLink {
  id:           number;
  token:        string;
  public_url:   string;
  access_level: string;
  label:        string;
  has_password: boolean;
  expires_at:   string;
  is_active:    boolean;
  is_valid:     boolean;
  use_count:    number;
  max_uses:     number | null;
  created_at:   string;
}

interface Props {
  documentId:     number;
  documentNumber: string;
  revisionId?:    number;
}

async function apiFetch(url: string, opts: RequestInit = {}) {
  const res = await fetch(url, { credentials: 'include', ...opts });
  return res.json();
}

export const ShareLinkModal: React.FC<Props> = ({
  documentId, documentNumber, revisionId,
}) => {
  const [open,      setOpen]      = useState(false);
  const [links,     setLinks]     = useState<ShareLink[]>([]);
  const [loading,   setLoading]   = useState(false);
  const [copied,    setCopied]    = useState<number | null>(null);
  const [error,     setError]     = useState<string | null>(null);

  // Create form state
  const [expiry,    setExpiry]    = useState(7);
  const [level,     setLevel]     = useState<'VIEW_FILE' | 'VIEW_METADATA'>('VIEW_FILE');
  const [label,     setLabel]     = useState('');
  const [maxUses,   setMaxUses]   = useState<string>('');
  const [password,  setPassword]  = useState('');

  const loadLinks = useCallback(async () => {
    const data = await apiFetch(
      `/api/v1/sharelinks/?document=${documentId}`
    );
    setLinks(Array.isArray(data) ? data : data.results ?? []);
  }, [documentId]);

  useEffect(() => { if (open) loadLinks(); }, [open, loadLinks]);

  const create = async () => {
    setLoading(true); setError(null);
    const body: any = {
      document_id:     documentId,
      expires_in_days: expiry,
      access_level:    level,
      label,
    };
    if (revisionId)             body.revision_id = revisionId;
    if (maxUses)                body.max_uses    = parseInt(maxUses, 10);
    if (password.trim())        body.password    = password;

    const res = await apiFetch('/api/v1/sharelinks/', {
      method:  'POST',
      headers: { 'Content-Type': 'application/json' },
      body:    JSON.stringify(body),
    });
    if (res.id) {
      setLabel(''); setPassword(''); setMaxUses('');
      await loadLinks();
    } else {
      setError(JSON.stringify(res));
    }
    setLoading(false);
  };

  const revoke = async (linkId: number) => {
    await apiFetch(`/api/v1/sharelinks/${linkId}/revoke/`, { method: 'POST' });
    await loadLinks();
  };

  const copy = (url: string, id: number) => {
    navigator.clipboard.writeText(url);
    setCopied(id);
    setTimeout(() => setCopied(null), 2000);
  };

  return (
    <>
      <button className="btn btn--secondary btn--sm" onClick={() => setOpen(true)}>
        🔗 Share
      </button>

      {open && (
        <div className="modal-overlay" onClick={() => setOpen(false)}>
          <div className="modal" onClick={e => e.stopPropagation()}>
            <div className="modal__header">
              <h3>🔗 Share — {documentNumber}</h3>
              <button className="modal__close" onClick={() => setOpen(false)}>✕</button>
            </div>

            <div className="modal__body">
              {/* Create new link */}
              <section className="share-create">
                <h4>Create new link</h4>
                <div className="share-create__row">
                  <label>Expires in
                    <select value={expiry} onChange={e => setExpiry(Number(e.target.value))}>
                      <option value={1}>1 day</option>
                      <option value={7}>7 days</option>
                      <option value={30}>30 days</option>
                      <option value={90}>90 days</option>
                    </select>
                  </label>
                  <label>Access
                    <select value={level} onChange={e => setLevel(e.target.value as any)}>
                      <option value="VIEW_FILE">View + Download</option>
                      <option value="VIEW_METADATA">Metadata only</option>
                    </select>
                  </label>
                </div>
                <div className="share-create__row">
                  <label>Label
                    <input type="text" value={label}
                      placeholder="e.g. Shared with RDSO"
                      onChange={e => setLabel(e.target.value)} />
                  </label>
                  <label>Max uses
                    <input type="number" value={maxUses} min={1}
                      placeholder="Unlimited"
                      onChange={e => setMaxUses(e.target.value)} />
                  </label>
                </div>
                <label>Password (optional)
                  <input type="password" value={password}
                    placeholder="Leave blank for no password"
                    onChange={e => setPassword(e.target.value)} />
                </label>
                {error && <p className="share-error">{error}</p>}
                <button className="btn btn--primary btn--sm"
                  onClick={create} disabled={loading}>
                  {loading ? 'Creating…' : '+ Create link'}
                </button>
              </section>

              {/* Existing links */}
              <section className="share-list">
                <h4>Existing links</h4>
                {links.length === 0 ? (
                  <p className="share-list__empty">No links yet.</p>
                ) : (
                  <ul className="share-list__items">
                    {links.map(link => (
                      <li key={link.id} className={`share-item${
                        !link.is_valid ? ' share-item--expired' : ''
                      }`}>
                        <div className="share-item__meta">
                          <span className="share-item__label">
                            {link.label || '(no label)'}
                          </span>
                          <span className="share-item__stats">
                            {link.access_level === 'VIEW_FILE' ? '📄' : '🔍'}
                            {' '}
                            {link.use_count}
                            {link.max_uses ? `/${link.max_uses}` : ''} uses
                            {' • '}
                            Expires {new Date(link.expires_at).toLocaleDateString()}
                            {link.has_password ? ' 🔒' : ''}
                          </span>
                        </div>
                        <div className="share-item__actions">
                          {link.is_valid ? (
                            <>
                              <button
                                className="btn btn--ghost btn--xs"
                                onClick={() => copy(link.public_url, link.id)}
                              >
                                {copied === link.id ? '✅ Copied!' : '📋 Copy URL'}
                              </button>
                              <button
                                className="btn btn--danger btn--xs"
                                onClick={() => revoke(link.id)}
                              >
                                Revoke
                              </button>
                            </>
                          ) : (
                            <span className="share-item__badge share-item__badge--expired">
                              {link.is_active ? 'Expired' : 'Revoked'}
                            </span>
                          )}
                        </div>
                      </li>
                    ))}
                  </ul>
                )}
              </section>
            </div>
          </div>
        </div>
      )}
    </>
  );
};

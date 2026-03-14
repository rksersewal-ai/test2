// =============================================================================
// FILE: frontend/src/components/totp/TotpVerify.tsx
// SPRINT 8 — 2FA verification screen shown after password login
//             when totp_required=true is returned.
// =============================================================================
import React, { useState } from 'react';

interface Props {
  refreshToken: string;               // partial JWT from password-login step
  onVerified:   (tokens: { access: string; refresh: string }) => void;
}

export const TotpVerify: React.FC<Props> = ({ refreshToken, onVerified }) => {
  const [code,    setCode]    = useState('');
  const [loading, setLoading] = useState(false);
  const [error,   setError]   = useState<string | null>(null);
  const [useBackup, setUseBackup] = useState(false);

  const verify = async () => {
    if (!code.trim()) { setError('Enter your code.'); return; }
    setLoading(true); setError(null);
    try {
      const res = await fetch('/api/v1/totp/verify-token/', {
        method:  'POST',
        headers: { 'Content-Type': 'application/json' },
        body:    JSON.stringify({ refresh_token: refreshToken, code }),
      });
      const data = await res.json();
      if (res.ok && data.access) {
        onVerified({ access: data.access, refresh: data.refresh });
      } else {
        setError(data.error ?? 'Verification failed.');
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="totp-verify">
      <h3 className="totp-verify__title">🔒 Two-Factor Authentication</h3>
      <p className="totp-verify__hint">
        {useBackup
          ? 'Enter one of your backup codes (e.g. A3F8C2).'
          : 'Enter the 6-digit code from your authenticator app.'}
      </p>

      <input
        type="text"
        inputMode={useBackup ? 'text' : 'numeric'}
        maxLength={useBackup ? 20 : 6}
        value={code}
        onChange={e => setCode(
          useBackup ? e.target.value : e.target.value.replace(/\D/g, '')
        )}
        className="totp-verify__input"
        placeholder={useBackup ? 'A3F8C2' : '123456'}
        autoComplete="one-time-code"
        autoFocus
      />

      {error && <p className="totp-verify__error">{error}</p>}

      <button
        className="btn btn--primary"
        onClick={verify}
        disabled={loading}
      >
        {loading ? 'Verifying…' : 'Verify'}
      </button>

      <button
        className="btn btn--ghost btn--sm totp-verify__backup-toggle"
        onClick={() => { setUseBackup(b => !b); setCode(''); setError(null); }}
      >
        {useBackup ? '← Use authenticator app instead' : 'Use a backup code'}
      </button>
    </div>
  );
};

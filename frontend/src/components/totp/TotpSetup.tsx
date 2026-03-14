// =============================================================================
// FILE: frontend/src/components/totp/TotpSetup.tsx
// SPRINT 8 — 2FA Setup wizard (3 steps)
//
// Step 1: Show QR code + manual secret entry instruction
// Step 2: Confirm with first 6-digit code
// Step 3: Display backup codes (shown ONCE, user must confirm saved)
// =============================================================================
import React, { useState } from 'react';

type Step = 1 | 2 | 3;

interface SetupData {
  secret:  string;
  qr_uri:  string;
}

async function api(url: string, body?: object) {
  const res = await fetch(url, {
    method:      'POST',
    credentials: 'include',
    headers:     body ? { 'Content-Type': 'application/json' } : undefined,
    body:        body ? JSON.stringify(body) : undefined,
  });
  return res.json();
}

export const TotpSetup: React.FC<{ onComplete?: () => void }> = ({ onComplete }) => {
  const [step,         setStep]         = useState<Step>(1);
  const [setupData,    setSetupData]    = useState<SetupData | null>(null);
  const [code,         setCode]         = useState('');
  const [backupCodes,  setBackupCodes]  = useState<string[]>([]);
  const [loading,      setLoading]      = useState(false);
  const [error,        setError]        = useState<string | null>(null);
  const [confirmed,    setConfirmed]    = useState(false);

  // Step 1: fetch QR
  const startSetup = async () => {
    setLoading(true); setError(null);
    const data = await api('/api/v1/totp/setup/');
    if (data.secret) {
      setSetupData(data);
      setStep(2);
    } else {
      setError(data.error ?? 'Setup failed.');
    }
    setLoading(false);
  };

  // Step 2: confirm code
  const confirmCode = async () => {
    if (code.length < 6) { setError('Enter 6-digit code.'); return; }
    setLoading(true); setError(null);
    const data = await api('/api/v1/totp/setup/confirm/', { code });
    if (data.backup_codes) {
      setBackupCodes(data.backup_codes);
      setStep(3);
    } else {
      setError(data.error ?? 'Confirmation failed.');
    }
    setLoading(false);
  };

  return (
    <div className="totp-setup">
      <h3 className="totp-setup__title">🔒 Set up Two-Factor Authentication</h3>

      {/* ---- Step 1: Intro ---- */}
      {step === 1 && (
        <div className="totp-setup__step">
          <p>Two-factor authentication adds a second layer of security using a
             time-based one-time password (TOTP) from your authenticator app
             (Google Authenticator, Authy, or any TOTP app).</p>
          <button className="btn btn--primary" onClick={startSetup} disabled={loading}>
            {loading ? 'Generating…' : 'Start 2FA setup'}
          </button>
          {error && <p className="totp-setup__error">{error}</p>}
        </div>
      )}

      {/* ---- Step 2: Scan QR ---- */}
      {step === 2 && setupData && (
        <div className="totp-setup__step">
          <p>Scan this QR code with your authenticator app:</p>
          <img
            src={setupData.qr_uri}
            alt="TOTP QR Code"
            className="totp-setup__qr"
          />
          <details className="totp-setup__manual">
            <summary>Can’t scan? Enter code manually</summary>
            <code className="totp-setup__secret">{setupData.secret}</code>
          </details>
          <label className="totp-setup__label">
            Enter the 6-digit code from your app:
            <input
              type="text"
              inputMode="numeric"
              maxLength={6}
              value={code}
              onChange={e => setCode(e.target.value.replace(/\D/g, ''))}
              className="totp-setup__code-input"
              placeholder="123456"
              autoComplete="one-time-code"
            />
          </label>
          {error && <p className="totp-setup__error">{error}</p>}
          <button className="btn btn--primary" onClick={confirmCode} disabled={loading}>
            {loading ? 'Verifying…' : 'Verify & Enable 2FA'}
          </button>
        </div>
      )}

      {/* ---- Step 3: Backup codes ---- */}
      {step === 3 && (
        <div className="totp-setup__step">
          <div className="totp-setup__success">✅ 2FA enabled successfully!</div>
          <p className="totp-setup__backup-warn">
            ⚠️ <strong>Save these backup codes now.</strong> Each can be used once
            if you lose access to your authenticator app. They will NOT be shown again.
          </p>
          <ul className="totp-setup__backup-codes">
            {backupCodes.map((c, i) => (
              <li key={i} className="totp-setup__backup-code">
                <code>{c}</code>
              </li>
            ))}
          </ul>
          <label className="totp-setup__confirm-label">
            <input
              type="checkbox"
              checked={confirmed}
              onChange={e => setConfirmed(e.target.checked)}
            />
            {' '}I have saved my backup codes in a safe place.
          </label>
          <button
            className="btn btn--success"
            disabled={!confirmed}
            onClick={() => onComplete?.()}
          >
            Done
          </button>
        </div>
      )}
    </div>
  );
};

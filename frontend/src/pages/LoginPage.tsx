// =============================================================================
// FILE: frontend/src/pages/LoginPage.tsx
// BUG FIX: Updated to use useAuth() (not useAuthContext directly).
// Added proper error display, loading state, and redirect if already logged in.
// =============================================================================
import { useState, FormEvent } from 'react';
import { useNavigate, Navigate } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';

export default function LoginPage() {
  const { login, isAuthenticated } = useAuth();
  const navigate = useNavigate();

  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error,    setError]    = useState('');
  const [loading,  setLoading]  = useState(false);

  // Already logged in — go to dashboard
  if (isAuthenticated) return <Navigate to="/" replace />;

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      await login(username, password);
      navigate('/', { replace: true });
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Login failed. Check credentials.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={styles.page}>
      <div style={styles.card}>
        <h1 style={styles.title}>EDMS-LDO</h1>
        <p style={styles.subtitle}>Electronic Document Management System</p>
        <p style={styles.org}>Locomotive Drawing Order — Indian Railways</p>

        <form onSubmit={handleSubmit} style={styles.form}>
          {error && <div style={styles.errorBox}>{error}</div>}

          <div style={styles.field}>
            <label style={styles.label}>Username</label>
            <input
              style={styles.input}
              type="text"
              value={username}
              onChange={e => setUsername(e.target.value)}
              autoComplete="username"
              autoFocus
              required
            />
          </div>

          <div style={styles.field}>
            <label style={styles.label}>Password</label>
            <input
              style={styles.input}
              type="password"
              value={password}
              onChange={e => setPassword(e.target.value)}
              autoComplete="current-password"
              required
            />
          </div>

          <button
            style={{ ...styles.button, opacity: loading ? 0.7 : 1 }}
            type="submit"
            disabled={loading}
          >
            {loading ? 'Signing in…' : 'Sign In'}
          </button>
        </form>
      </div>
    </div>
  );
}

const styles: Record<string, React.CSSProperties> = {
  page      : { minHeight: '100vh', display: 'flex', alignItems: 'center',
                justifyContent: 'center', background: '#0f172a' },
  card      : { background: '#1e293b', borderRadius: 12, padding: '2.5rem 2rem',
                width: 360, boxShadow: '0 8px 32px rgba(0,0,0,0.4)' },
  title     : { color: '#f8fafc', fontSize: 24, fontWeight: 700,
                margin: 0, textAlign: 'center', letterSpacing: 1 },
  subtitle  : { color: '#94a3b8', fontSize: 13, textAlign: 'center', margin: '4px 0 2px' },
  org       : { color: '#475569', fontSize: 11, textAlign: 'center', marginBottom: '1.5rem' },
  form      : { display: 'flex', flexDirection: 'column', gap: '1rem' },
  errorBox  : { background: '#450a0a', color: '#fca5a5', padding: '0.6rem 0.8rem',
                borderRadius: 6, fontSize: 13 },
  field     : { display: 'flex', flexDirection: 'column', gap: 4 },
  label     : { color: '#94a3b8', fontSize: 13, fontWeight: 500 },
  input     : { background: '#0f172a', border: '1px solid #334155', borderRadius: 6,
                padding: '0.5rem 0.75rem', color: '#f8fafc', fontSize: 14, outline: 'none' },
  button    : { background: '#2563eb', color: '#fff', border: 'none', borderRadius: 6,
                padding: '0.65rem', fontSize: 15, fontWeight: 600,
                cursor: 'pointer', marginTop: 4 },
};

import { useState } from 'react';
import { useAuthStore, decodeJwtPayload } from './authStore';

const BFF = import.meta.env.VITE_BFF_URL || 'http://localhost:8009';

export default function LoginModal({ onClose }) {
  const { login } = useAuthStore();
  const [tab, setTab] = useState('login');
  const [username, setUsername] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState('');
  const [showPassword, setShowPassword] = useState(false);

  const resetForm = () => {
    setUsername('');
    setEmail('');
    setPassword('');
    setError('');
    setSuccess('');
    setShowPassword(false);
  };

  const switchTab = (t) => {
    setTab(t);
    resetForm();
  };

  const handleLogin = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      const body = new URLSearchParams({ username: username.trim(), password });
      const res = await fetch(`${BFF}/api/auth/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: body.toString(),
      });
      if (!res.ok) {
        const data = await res.json().catch(() => ({}));
        setError(res.status === 401 ? 'Usuario o contraseña incorrectos.' : (data.detail || 'Error al iniciar sesión.'));
        return;
      }
      const data = await res.json();
      const payload = decodeJwtPayload(data.access_token);
      login(data.access_token, data.refresh_token, {
        username: String(payload.sub ?? username),
        role: String(payload.role ?? 'user'),
        user_id: String(payload.user_id ?? ''),
      });
      onClose();
    } catch {
      setError('Sin conexión al servidor. Intenta de nuevo.');
    } finally {
      setLoading(false);
    }
  };

  const handleRegister = async (e) => {
    e.preventDefault();
    setError('');
    if (password.length < 6) {
      setError('La contraseña debe tener al menos 6 caracteres.');
      return;
    }
    setLoading(true);
    try {
      const res = await fetch(`${BFF}/api/auth/register`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username: username.trim(), email: email.trim(), password }),
      });
      if (!res.ok) {
        const data = await res.json().catch(() => ({}));
        setError(data.detail || 'Error al registrarse. Intenta con otro usuario o correo.');
        return;
      }
      setSuccess(`¡Cuenta creada! Inicia sesión con "${username.trim()}".`);
      setTab('login');
      setUsername(username.trim());
      setPassword('');
      setEmail('');
      setError('');
    } catch {
      setError('Sin conexión al servidor. Intenta de nuevo.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div
      onClick={onClose}
      style={{
        position: 'fixed', inset: 0, zIndex: 1000,
        background: 'rgba(0,0,0,0.72)',
        display: 'flex', alignItems: 'center', justifyContent: 'center',
        padding: 20,
        backdropFilter: 'blur(6px)',
      }}
    >
      <div
        onClick={(e) => e.stopPropagation()}
        style={{
          width: '100%', maxWidth: 400,
          background: '#16171d',
          border: '1px solid #2a2c35',
          borderRadius: 16,
          overflow: 'hidden',
          boxShadow: '0 32px 80px rgba(0,0,0,0.6)',
          animation: 'modalIn 0.22s cubic-bezier(0.16,1,0.3,1)',
        }}
      >
        {/* Header */}
        <div style={{
          display: 'flex', alignItems: 'center', justifyContent: 'space-between',
          padding: '20px 24px 0',
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
            <span style={{ fontSize: '1.2rem' }}>🎮</span>
            <span style={{ fontWeight: 800, fontSize: '0.95rem', color: '#f7f8fa', letterSpacing: '-0.01em' }}>TechFlow</span>
          </div>
          <button
            onClick={onClose}
            style={{
              background: '#2a2c35', border: 'none', borderRadius: 8,
              width: 30, height: 30, cursor: 'pointer',
              display: 'flex', alignItems: 'center', justifyContent: 'center',
              color: '#8f92a1', fontSize: '0.8rem', fontWeight: 700,
              transition: 'background 0.15s',
            }}
            aria-label="Cerrar"
          >
            ✕
          </button>
        </div>

        {/* Tabs */}
        <div style={{
          display: 'flex', margin: '18px 24px 0',
          background: '#0f1117', borderRadius: 10, padding: 3,
          border: '1px solid #2a2c35',
        }}>
          {['login', 'register'].map((t) => (
            <button
              key={t}
              onClick={() => switchTab(t)}
              style={{
                flex: 1, padding: '8px 0',
                border: 'none',
                background: tab === t ? '#2a2c35' : 'transparent',
                fontWeight: 600, fontSize: '0.82rem',
                cursor: 'pointer',
                color: tab === t ? '#f7f8fa' : '#6b6e7e',
                borderRadius: 8,
                transition: 'all 0.15s',
                fontFamily: 'inherit',
              }}
            >
              {t === 'login' ? 'Iniciar sesión' : 'Crear cuenta'}
            </button>
          ))}
        </div>

        <div style={{ padding: '22px 24px 26px' }}>
          {success && tab === 'login' && (
            <div style={{
              background: 'rgba(245,158,11,0.1)', border: '1px solid rgba(245,158,11,0.3)',
              borderRadius: 10, padding: '10px 14px',
              color: '#f59e0b', fontSize: '0.83rem',
              display: 'flex', gap: 8, alignItems: 'flex-start',
              marginBottom: 16,
            }}>
              <span style={{ flexShrink: 0 }}>✓</span>
              <span>{success}</span>
            </div>
          )}

          {tab === 'login' ? (
            <form onSubmit={handleLogin}>
              <div style={{ marginBottom: 14 }}>
                <label style={labelStyle}>Nombre de usuario</label>
                <input
                  type="text"
                  placeholder="ej: juanmoya"
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  required
                  autoFocus={!success}
                  autoComplete="username"
                  style={{ ...inputStyle, borderColor: error ? '#7f1d1d' : undefined }}
                />
              </div>
              <div style={{ marginBottom: 16, position: 'relative' }}>
                <label style={labelStyle}>Contraseña</label>
                <div style={{ position: 'relative' }}>
                  <input
                    type={showPassword ? 'text' : 'password'}
                    placeholder="Tu contraseña"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    required
                    autoComplete="current-password"
                    style={{ ...inputStyle, borderColor: error ? '#7f1d1d' : undefined, paddingRight: 44 }}
                  />
                  <button
                    type="button"
                    onClick={() => setShowPassword(!showPassword)}
                    style={{
                      position: 'absolute', right: 12, top: '50%', transform: 'translateY(-50%)',
                      background: 'none', border: 'none', cursor: 'pointer',
                      color: '#6b6e7e', fontSize: '0.85rem', padding: 0,
                    }}
                    tabIndex={-1}
                  >
                    {showPassword ? '🙈' : '👁️'}
                  </button>
                </div>
              </div>

              {error && <ErrorMsg>{error}</ErrorMsg>}

              <button type="submit" disabled={loading || !username.trim() || !password} style={btnPrimary(loading)}>
                {loading ? 'Verificando...' : 'Entrar'}
              </button>

              <p style={{ textAlign: 'center', color: '#525461', fontSize: '0.78rem', marginTop: 16, marginBottom: 0 }}>
                ¿No tienes cuenta?{' '}
                <button type="button" onClick={() => switchTab('register')} style={linkBtn}>
                  Créala gratis
                </button>
              </p>
            </form>
          ) : (
            <form onSubmit={handleRegister}>
              <div style={{ marginBottom: 14 }}>
                <label style={labelStyle}>Nombre de usuario</label>
                <input
                  type="text"
                  placeholder="ej: juanmoya"
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  required
                  autoFocus
                  autoComplete="username"
                  style={inputStyle}
                />
                <span style={hintStyle}>Sin espacios ni caracteres especiales</span>
              </div>
              <div style={{ marginBottom: 14 }}>
                <label style={labelStyle}>Correo electrónico</label>
                <input
                  type="email"
                  placeholder="tu@correo.com"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  required
                  autoComplete="email"
                  style={inputStyle}
                />
              </div>
              <div style={{ marginBottom: 16, position: 'relative' }}>
                <label style={labelStyle}>Contraseña</label>
                <div style={{ position: 'relative' }}>
                  <input
                    type={showPassword ? 'text' : 'password'}
                    placeholder="Mínimo 6 caracteres"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    required
                    minLength={6}
                    autoComplete="new-password"
                    style={{ ...inputStyle, paddingRight: 44 }}
                  />
                  <button
                    type="button"
                    onClick={() => setShowPassword(!showPassword)}
                    style={{
                      position: 'absolute', right: 12, top: '50%', transform: 'translateY(-50%)',
                      background: 'none', border: 'none', cursor: 'pointer',
                      color: '#6b6e7e', fontSize: '0.85rem', padding: 0,
                    }}
                    tabIndex={-1}
                  >
                    {showPassword ? '🙈' : '👁️'}
                  </button>
                </div>
                {password.length > 0 && password.length < 6 && (
                  <span style={{ ...hintStyle, color: '#f59e0b' }}>
                    Faltan {6 - password.length} caracteres más
                  </span>
                )}
              </div>

              {error && <ErrorMsg>{error}</ErrorMsg>}

              <button
                type="submit"
                disabled={loading || !username.trim() || !email.trim() || password.length < 6}
                style={btnPrimary(loading || password.length < 6)}
              >
                {loading ? 'Creando cuenta...' : 'Crear cuenta gratis'}
              </button>

              <p style={{ textAlign: 'center', color: '#525461', fontSize: '0.78rem', marginTop: 16, marginBottom: 0 }}>
                ¿Ya tienes cuenta?{' '}
                <button type="button" onClick={() => switchTab('login')} style={linkBtn}>
                  Inicia sesión
                </button>
              </p>
            </form>
          )}
        </div>
      </div>

      <style>{`
        @keyframes modalIn {
          from { opacity: 0; transform: translateY(14px) scale(0.97); }
          to   { opacity: 1; transform: translateY(0) scale(1); }
        }
      `}</style>
    </div>
  );
}

function ErrorMsg({ children }) {
  return (
    <div style={{
      background: 'rgba(239,68,68,0.1)', border: '1px solid rgba(239,68,68,0.3)',
      borderRadius: 10, padding: '10px 14px',
      color: '#f87171', fontSize: '0.83rem',
      display: 'flex', gap: 8, alignItems: 'flex-start',
      marginBottom: 14,
    }}>
      <span style={{ flexShrink: 0 }}>⚠</span>
      <span>{children}</span>
    </div>
  );
}

const labelStyle = {
  display: 'block',
  color: '#b8bac4',
  fontSize: '0.78rem',
  fontWeight: 600,
  marginBottom: 6,
  letterSpacing: '0.02em',
};

const inputStyle = {
  display: 'block', width: '100%',
  padding: '11px 14px',
  border: '1.5px solid rgba(6,182,212,0.25)',
  borderRadius: 10,
  fontSize: '0.88rem',
  outline: 'none',
  boxSizing: 'border-box',
  color: '#e0e9ff',
  fontFamily: 'inherit',
  background: '#0d1117',
  transition: 'border-color 0.15s, box-shadow 0.15s',
};

const hintStyle = {
  display: 'block',
  color: '#525461',
  fontSize: '0.73rem',
  marginTop: 4,
};

const btnPrimary = (disabled) => ({
  display: 'block', width: '100%',
  padding: '12px',
  background: disabled ? '#16202b' : '#06b6d4',
  color: disabled ? '#6b6e7e' : '#0f1117',
  border: 'none', borderRadius: 10,
  fontSize: '0.88rem', fontWeight: 700,
  cursor: disabled ? 'not-allowed' : 'pointer',
  fontFamily: 'inherit',
  transition: 'all 0.15s',
  boxShadow: disabled ? 'none' : '0 8px 20px rgba(6,182,212,0.3)',
  letterSpacing: '0.01em',
});

const linkBtn = {
  color: '#06b6d4',
  background: 'none',
  border: 'none',
  cursor: 'pointer',
  fontWeight: 700,
  padding: 0,
  fontFamily: 'inherit',
  fontSize: 'inherit',
};

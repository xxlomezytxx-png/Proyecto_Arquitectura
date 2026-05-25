import { useState, FormEvent } from 'react';
import { Mail, Lock, ArrowRight, Eye, EyeOff, Sparkles, ShieldCheck, BookOpen, BarChart3 } from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';
import { Logo, Wordmark, Btn, Field, Input } from '../components/ui';

const BFF = import.meta.env.VITE_BFF_URL || 'http://localhost:8009';

function decodeJwtPayload(token: string): Record<string, unknown> {
  try {
    const base64 = token.split('.')[1].replace(/-/g, '+').replace(/_/g, '/');
    return JSON.parse(atob(base64)) as Record<string, unknown>;
  } catch {
    return {};
  }
}

function SsoIcon({ kind }: { kind: 'google' | 'sso' }) {
  if (kind === 'google') return (
    <svg width="14" height="14" viewBox="0 0 18 18">
      <path fill="#4285F4" d="M17.64 9.2c0-.64-.06-1.25-.16-1.84H9v3.49h4.84a4.14 4.14 0 0 1-1.79 2.72v2.26h2.9c1.7-1.57 2.69-3.88 2.69-6.63z"/>
      <path fill="#34A853" d="M9 18c2.43 0 4.47-.8 5.96-2.18l-2.9-2.26c-.8.54-1.83.86-3.06.86-2.35 0-4.34-1.59-5.05-3.71H.96v2.33A9 9 0 0 0 9 18z"/>
      <path fill="#FBBC04" d="M3.95 10.71A5.4 5.4 0 0 1 3.66 9c0-.59.1-1.17.29-1.71V4.96H.96A9 9 0 0 0 0 9c0 1.45.35 2.82.96 4.04l2.99-2.33z"/>
      <path fill="#EA4335" d="M9 3.58c1.32 0 2.5.45 3.44 1.34l2.58-2.58C13.46.89 11.43 0 9 0A9 9 0 0 0 .96 4.96l2.99 2.33C4.66 5.17 6.65 3.58 9 3.58z"/>
    </svg>
  );
  return (
    <svg width="14" height="14" viewBox="0 0 16 16" fill="none" stroke="#0f1117" strokeWidth="1.6">
      <rect x="1.5" y="3.5" width="13" height="9" rx="1.5"/>
      <path d="M4 7.5h3M4 9.5h5M11 7l1.6 1.6L11 10.2" strokeLinecap="round" strokeLinejoin="round"/>
    </svg>
  );
}

const STATS = [
  { Icon: BookOpen,  label: 'Catálogo',      value: '12,480', sub: 'ítems',      amber: false },
  { Icon: Sparkles,  label: 'Enriquecidos',  value: '73.8%',  sub: 'por IA',     amber: true  },
  { Icon: BarChart3, label: 'Precio óptimo', value: '94%',    sub: 'explicable', amber: false },
];

export default function LoginPage() {
  const { login } = useAuth();
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [showInfo, setShowInfo] = useState(false);
  const [showPassword, setShowPassword] = useState(false);

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    if (!username.trim() || !password) return;
    setError('');
    setLoading(true);

    try {
      const formBody = new URLSearchParams({ username: username.trim(), password });
      const res = await fetch(`${BFF}/api/auth/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: formBody.toString(),
      });

      if (!res.ok) {
        const data = await res.json().catch(() => ({}));
        const msg = (data as { detail?: string }).detail;
        if (res.status === 401) {
          setError('Usuario o contraseña incorrectos. Verifica tus credenciales.');
        } else if (res.status === 404 || res.status === 422) {
          setError('No se pudo conectar con el servidor de autenticación. ¿El backend está activo?');
        } else {
          setError(msg || 'Error al iniciar sesión. Intenta de nuevo.');
        }
        return;
      }

      const data = await res.json() as {
        access_token: string;
        refresh_token: string;
        token_type: string;
        role: string;
      };

      const payload = decodeJwtPayload(data.access_token);

      if (payload.role !== 'admin') {
        setError('Tu cuenta no tiene permisos de administrador. Contacta al equipo técnico para que asignen el rol admin.');
        return;
      }

      login(data.access_token, data.refresh_token, {
        username: String(payload.sub ?? username),
        role: String(payload.role ?? 'user'),
        user_id: String(payload.user_id ?? ''),
      });
    } catch {
      setError('Sin conexión al servidor. Verifica que el backend esté activo (docker-compose up).');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="grid h-screen w-full grid-cols-1 lg:grid-cols-[1.05fr_1fr] bg-white">
      {/* LEFT — brand panel */}
      <div className="relative hidden lg:flex flex-col justify-between overflow-hidden bg-ink-900 text-white p-10">
        <div className="absolute inset-0 grid-bg opacity-60" />
        <div
          className="absolute -top-40 -right-40 h-[480px] w-[480px] rounded-full"
          style={{ background: 'radial-gradient(closest-side, rgba(245,158,11,.55), transparent 70%)' }}
        />
        <div
          className="absolute bottom-[-220px] left-[-160px] h-[520px] w-[520px] rounded-full"
          style={{ background: 'radial-gradient(closest-side, rgba(63,67,80,.9), transparent 70%)' }}
        />

        <div className="relative z-10 flex items-center gap-2.5">
          <Logo size={26} mono />
          <div className="leading-none">
            <div className="text-[15px] font-semibold tracking-tight">TechFlow</div>
            <div className="text-[10px] tracking-[.18em] uppercase text-white/50 -mt-px">AI Commerce</div>
          </div>
        </div>

        <div className="relative z-10 max-w-[460px]">
          <div className="inline-flex items-center gap-1.5 rounded-full bg-white/10 px-2.5 py-1 text-[11px] font-medium text-amber-200 ring-1 ring-inset ring-amber-300/30">
            <Sparkles size={12} strokeWidth={2.2} />
            v3 · Pricing inteligente
          </div>
          <h1 className="mt-5 font-serif text-[56px] leading-[1.02] tracking-tight">
            Transforma tu inventario con <span className="text-amber-300">IA</span>.
          </h1>
          <p className="mt-4 text-[14.5px] leading-relaxed text-white/70 max-w-[420px]">
            De hojas de cálculo dispersas a un catálogo comercial enriquecido, con precios sugeridos
            explicables y atención asistida — listo para vender.
          </p>

          <div className="mt-9 grid grid-cols-3 gap-3 max-w-[420px]">
            {STATS.map(({ Icon, label, value, sub, amber }) => (
              <div key={label} className="rounded-xl bg-white/[.04] ring-1 ring-white/10 p-3 backdrop-blur">
                <Icon size={14} className={amber ? 'text-amber-300' : 'text-white/60'} strokeWidth={2} />
                <div className="mt-2 text-[10px] uppercase tracking-[.16em] text-white/45">{label}</div>
                <div className="num text-[20px] font-semibold leading-tight">{value}</div>
                <div className="text-[10.5px] text-white/55">{sub}</div>
              </div>
            ))}
          </div>
        </div>

        <div className="relative z-10 flex items-center justify-between text-[11px] text-white/50">
          <div className="inline-flex items-center gap-1.5">
            <ShieldCheck size={13} /> SOC 2 · ISO 27001 · GDPR
          </div>
          <div>© 2026 TechFlow Labs</div>
        </div>
      </div>

      {/* RIGHT — form */}
      <div className="flex items-center justify-center px-6 py-10 sm:px-12">
        <form onSubmit={handleSubmit} className="w-full max-w-[400px] float-in">
          <div className="lg:hidden mb-8"><Wordmark /></div>
          <div className="text-[11px] uppercase tracking-[.2em] text-ink-400">Acceso para operadores</div>
          <h2 className="mt-2 font-serif text-[36px] leading-tight tracking-tight">Inicia sesión</h2>
          <p className="mt-1.5 text-[13.5px] text-ink-500">
            Bienvenido de vuelta. Ingresa con tu cuenta de administrador.
          </p>

          <div className="mt-7 space-y-4">
            <Field label="Nombre de usuario" hint={<span className="text-ink-400">Solo el nombre, no el correo</span>}>
              <Input
                leftIcon={Mail}
                type="text"
                autoComplete="username"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                placeholder="ej: admin"
                required
                autoFocus
              />
            </Field>

            <Field label="Contraseña">
              <Input
                leftIcon={Lock}
                type={showPassword ? 'text' : 'password'}
                autoComplete="current-password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••"
                required
                rightSlot={
                  <button
                    type="button"
                    onClick={() => setShowPassword(v => !v)}
                    className="mr-1 inline-flex h-9 w-9 items-center justify-center rounded-md text-ink-400 hover:text-ink-900 hover:bg-ink-100"
                  >
                    {showPassword ? <EyeOff size={15} /> : <Eye size={15} />}
                  </button>
                }
              />
            </Field>

            {error && (
              <div className="rounded-lg bg-rose-50 px-3 py-2.5 text-[13px] text-rose-700 ring-1 ring-inset ring-rose-200">
                {error}
              </div>
            )}

            <Btn
              size="lg"
              iconRight={ArrowRight}
              className="w-full"
              disabled={loading || !username.trim() || !password}
            >
              {loading ? 'Verificando…' : 'Entrar al panel'}
            </Btn>

            <div className="relative my-2">
              <div className="absolute inset-0 flex items-center">
                <div className="w-full border-t border-ink-200" />
              </div>
              <div className="relative flex justify-center">
                <span className="bg-white px-3 text-[11px] uppercase tracking-[.18em] text-ink-400">o continúa con</span>
              </div>
            </div>

            <div className="grid grid-cols-2 gap-3">
              <Btn type="button" variant="secondary" size="md" className="w-full gap-2">
                <SsoIcon kind="google" /> Google Workspace
              </Btn>
              <Btn type="button" variant="secondary" size="md" className="w-full gap-2">
                <SsoIcon kind="sso" /> SSO / SAML
              </Btn>
            </div>
          </div>

          <div className="mt-6 rounded-lg bg-ink-50 px-3 py-2.5 text-[12.5px] text-ink-500 ring-1 ring-inset ring-ink-200">
            <button
              type="button"
              onClick={() => setShowInfo(v => !v)}
              className="flex w-full items-center gap-1.5 font-medium text-ink-700"
            >
              <span>{showInfo ? '▼' : '▶'}</span>
              ¿Primera vez? Cómo crear una cuenta admin
            </button>
            {showInfo && (
              <div className="mt-2.5 space-y-2 leading-relaxed">
                <p>
                  No existe un usuario por defecto. Créalo con este comando (requiere que el backend esté activo):
                </p>
                <code className="block rounded bg-ink-900 px-3 py-2 font-mono text-[11.5px] text-amber-300 break-all whitespace-pre-wrap">
                  {`curl -X POST http://localhost:8009/api/auth/register \\\n  -H "Content-Type: application/json" \\\n  -d '{"username":"admin","email":"admin@TechFlow.com","password":"Admin123!","role":"admin"}'`}
                </code>
                <p>
                  Después inicia sesión con <strong>admin</strong> y la contraseña que elegiste.
                </p>
              </div>
            )}
          </div>

          <p className="mt-6 text-[12px] text-center text-ink-400">
            Solo cuentas con rol <strong className="text-ink-600">admin</strong> pueden acceder a este panel
          </p>
        </form>
      </div>
    </div>
  );
}

import { Sparkles } from 'lucide-react';
import type { LucideIcon } from 'lucide-react';

// ── Logo ──────────────────────────────────────────────────────────────────────
interface LogoProps { size?: number; mono?: boolean; className?: string }
export function Logo({ size = 28, mono = false, className = '' }: LogoProps) {
  const c1 = mono ? 'currentColor' : '#0f1117';
  const c2 = mono ? 'currentColor' : '#f59e0b';
  return (
    <svg width={size} height={size} viewBox="0 0 32 32" className={className} aria-label="TechFlow">
      <rect x="3" y="6" width="26" height="20" rx="3" fill="none" stroke={c1} strokeWidth="1.6"/>
      <line x1="16" y1="6" x2="16" y2="26" stroke={c1} strokeWidth="1.6"/>
      <line x1="7"  y1="12" x2="13" y2="12" stroke={c1} strokeWidth="1.4" strokeLinecap="round"/>
      <line x1="7"  y1="16" x2="13" y2="16" stroke={c1} strokeWidth="1.4" strokeLinecap="round"/>
      <line x1="19" y1="12" x2="25" y2="12" stroke={c1} strokeWidth="1.4" strokeLinecap="round"/>
      <line x1="19" y1="16" x2="25" y2="16" stroke={c1} strokeWidth="1.4" strokeLinecap="round"/>
      <circle cx="22" cy="22" r="3" fill={c2}/>
      <circle cx="22" cy="22" r="1.1" fill={c1}/>
    </svg>
  );
}

// ── Wordmark ──────────────────────────────────────────────────────────────────
interface WordmarkProps { className?: string }
export function Wordmark({ className = '' }: WordmarkProps) {
  return (
    <div className={`flex items-center gap-2 ${className}`}>
      <Logo size={22} />
      <div className="leading-none">
        <div className="text-[15px] font-semibold tracking-tight text-ink-900">TechFlow</div>
        <div className="text-[10px] tracking-[.18em] uppercase text-ink-400 -mt-px">AI Commerce</div>
      </div>
    </div>
  );
}

// ── Badge ─────────────────────────────────────────────────────────────────────
type BadgeTone = 'neutral' | 'success' | 'warn' | 'danger' | 'ai' | 'invert';
interface BadgeProps { tone?: BadgeTone; children: React.ReactNode; dot?: boolean; className?: string }
export function Badge({ tone = 'neutral', children, dot = false, className = '' }: BadgeProps) {
  const tones: Record<BadgeTone, string> = {
    neutral: 'bg-ink-100 text-ink-700 ring-ink-200',
    success: 'bg-emerald-50 text-emerald-700 ring-emerald-200',
    warn:    'bg-amber-50 text-amber-600 ring-amber-200',
    danger:  'bg-rose-50 text-rose-700 ring-rose-200',
    ai:      'bg-amber-50 text-amber-600 ring-amber-200',
    invert:  'bg-ink-900 text-white ring-ink-800',
  };
  const dots: Record<BadgeTone, string> = {
    success: 'bg-emerald-500', warn: 'bg-amber-400',  danger: 'bg-rose-500',
    neutral: 'bg-ink-400',     ai:   'bg-amber-400',  invert: 'bg-amber-300',
  };
  return (
    <span className={`inline-flex items-center gap-1.5 rounded-full px-2 py-0.5 text-[11px] font-medium ring-1 ring-inset ${tones[tone]} ${className}`}>
      {dot && <span className={`h-1.5 w-1.5 rounded-full ${dots[tone]}`} />}
      {children}
    </span>
  );
}

// ── Sparkline ─────────────────────────────────────────────────────────────────
interface SparklineProps { data: number[]; color?: string; className?: string }
export function Sparkline({ data, color = '#0f1117', className = '' }: SparklineProps) {
  const w = 88, h = 28, pad = 2;
  const min = Math.min(...data), max = Math.max(...data);
  const norm = (v: number) => h - pad - ((v - min) / (max - min || 1)) * (h - pad * 2);
  const step = (w - pad * 2) / (data.length - 1);
  const d = data.map((v, i) => `${i ? 'L' : 'M'}${pad + i * step},${norm(v)}`).join(' ');
  const area = `${d} L${w - pad},${h} L${pad},${h} Z`;
  return (
    <svg width={w} height={h} className={className} viewBox={`0 0 ${w} ${h}`}>
      <path d={area} fill={color} opacity=".06" />
      <path d={d} fill="none" stroke={color} strokeWidth="1.4" strokeLinejoin="round" strokeLinecap="round"/>
    </svg>
  );
}

// ── IconBtn ───────────────────────────────────────────────────────────────────
interface IconBtnProps { icon: LucideIcon; label: string; onClick?: () => void; active?: boolean; className?: string }
export function IconBtn({ icon: Icon, label, onClick, active = false, className = '' }: IconBtnProps) {
  return (
    <button
      onClick={onClick}
      title={label}
      aria-label={label}
      className={`inline-flex h-9 w-9 items-center justify-center rounded-lg transition ${
        active ? 'bg-ink-900 text-white' : 'text-ink-500 hover:bg-ink-100 hover:text-ink-900'
      } ${className}`}
    >
      <Icon size={16} strokeWidth={1.8} />
    </button>
  );
}

// ── Field ─────────────────────────────────────────────────────────────────────
interface FieldProps { label: string; hint?: React.ReactNode; children: React.ReactNode; error?: string }
export function Field({ label, hint, children, error }: FieldProps) {
  return (
    <label className="block">
      <div className="mb-1.5 flex items-baseline justify-between">
        <span className="text-[12px] font-medium text-ink-700">{label}</span>
        {hint && <span className="text-[11px] text-ink-400">{hint}</span>}
      </div>
      {children}
      {error && <div className="mt-1 text-[11px] text-rose-600">{error}</div>}
    </label>
  );
}

// ── Input ─────────────────────────────────────────────────────────────────────
interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  leftIcon?: LucideIcon;
  rightSlot?: React.ReactNode;
}
export function Input({ leftIcon: L, rightSlot, ...props }: InputProps) {
  return (
    <div className="group flex items-center rounded-lg bg-white ring-1 ring-ink-200 focus-within:ring-2 focus-within:ring-ink-900 transition">
      {L && <L size={15} strokeWidth={1.8} className="ml-3 text-ink-400 group-focus-within:text-ink-700" />}
      <input
        {...props}
        className={`min-w-0 flex-1 bg-transparent px-3 py-2.5 text-[13.5px] text-ink-900 placeholder:text-ink-400 outline-none ${L ? 'pl-2' : ''}`}
      />
      {rightSlot}
    </div>
  );
}

// ── Btn ───────────────────────────────────────────────────────────────────────
type BtnVariant = 'primary' | 'secondary' | 'ghost' | 'ai' | 'danger';
type BtnSize    = 'sm' | 'md' | 'lg';
interface BtnProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: BtnVariant;
  size?: BtnSize;
  icon?: LucideIcon;
  iconRight?: LucideIcon;
  children?: React.ReactNode;
}
export function Btn({ variant = 'primary', size = 'md', icon: Icon, iconRight: IconR, children, className = '', ...props }: BtnProps) {
  const variants: Record<BtnVariant, string> = {
    primary:   'bg-ink-900 text-white hover:bg-ink-800 active:bg-ink-950 shadow-sm',
    secondary: 'bg-white text-ink-900 ring-1 ring-ink-200 hover:bg-ink-50',
    ghost:     'text-ink-700 hover:bg-ink-100',
    ai:        'bg-amber-400 text-ink-900 hover:bg-amber-300 ring-1 ring-amber-500/40 shadow-sm',
    danger:    'bg-rose-600 text-white hover:bg-rose-500',
  };
  const sizes: Record<BtnSize, string> = {
    sm: 'h-8 px-3 text-[12.5px] gap-1.5 rounded-md',
    md: 'h-10 px-4 text-[13.5px] gap-2 rounded-lg',
    lg: 'h-11 px-5 text-[14px] gap-2 rounded-lg',
  };
  const iconSize = size === 'sm' ? 14 : 16;
  return (
    <button
      {...props}
      className={`inline-flex items-center justify-center font-medium transition ${variants[variant]} ${sizes[size]} ${className}`}
    >
      {Icon && <Icon size={iconSize} strokeWidth={2}/>}
      {children}
      {IconR && <IconR size={iconSize} strokeWidth={2}/>}
    </button>
  );
}

// ── Checkbox ──────────────────────────────────────────────────────────────────
interface CheckboxProps { checked: boolean; onChange: (e: React.ChangeEvent<HTMLInputElement>) => void; label: string; count?: number }
export function Checkbox({ checked, onChange, label, count }: CheckboxProps) {
  return (
    <label className="flex cursor-pointer items-center justify-between gap-3 py-1.5 group">
      <span className="flex items-center gap-2.5">
        <span className={`grid h-4 w-4 place-items-center rounded border transition ${checked ? 'border-ink-900 bg-ink-900' : 'border-ink-300 bg-white group-hover:border-ink-500'}`}>
          {checked && (
            <svg viewBox="0 0 12 12" className="h-2.5 w-2.5 text-white" fill="none" stroke="currentColor" strokeWidth="2.4" strokeLinecap="round" strokeLinejoin="round">
              <polyline points="2.5,6.5 5,9 10,3.5"/>
            </svg>
          )}
        </span>
        <span className="text-[13px] text-ink-700 group-hover:text-ink-900">{label}</span>
      </span>
      {count !== undefined && <span className="text-[11px] num text-ink-400">{count}</span>}
      <input type="checkbox" checked={checked} onChange={onChange} className="sr-only"/>
    </label>
  );
}

// ── CoverPlaceholder ──────────────────────────────────────────────────────────
interface BookRef { tone?: string; edition?: string; author?: string; title?: string; year?: string | number; id?: string; aiPick?: boolean }
interface CoverPlaceholderProps { book: BookRef; w?: string | number; h?: number }
export function CoverPlaceholder({ book, w = '100%', h = 220 }: CoverPlaceholderProps) {
  return (
    <div
      className="relative overflow-hidden rounded-md ring-1 ring-ink-200/70"
      style={{ width: w, height: h, background: book.tone || '#3f4350' }}
    >
      <div className="absolute inset-0 opacity-[.07]"
           style={{ backgroundImage: 'repeating-linear-gradient(135deg, #fff 0 1px, transparent 1px 9px)' }} />
      <div className="absolute inset-0 flex flex-col p-4 text-white">
        <div className="text-[9px] tracking-[.22em] uppercase opacity-70">{book.edition || 'Edición'}</div>
        <div className="mt-auto">
          <div className="text-[10px] uppercase tracking-[.18em] opacity-70">{book.author}</div>
          <div className="font-serif text-[22px] leading-[1.05] mt-1 text-balance">{book.title}</div>
          <div className="mt-3 flex items-center justify-between text-[10px] opacity-70">
            <span className="num">{book.year}</span>
            <span>{book.id}</span>
          </div>
        </div>
      </div>
      {book.aiPick && (
        <div className="absolute top-2 right-2 inline-flex items-center gap-1 rounded-full bg-amber-400/95 px-2 py-0.5 text-[10px] font-semibold text-ink-900">
          <Sparkles size={10} strokeWidth={2.4} /> IA pick
        </div>
      )}
    </div>
  );
}

// ── AIConfidence ──────────────────────────────────────────────────────────────
interface AIConfidenceProps { value: number }
export function AIConfidence({ value }: AIConfidenceProps) {
  const pct = Math.round(value * 100);
  const tone = value > 0.85 ? 'bg-emerald-500' : value > 0.6 ? 'bg-amber-400' : 'bg-rose-500';
  return (
    <div className="flex items-center gap-2">
      <div className="h-1.5 w-12 overflow-hidden rounded-full bg-ink-100">
        <div className={`h-full ${tone}`} style={{ width: `${pct}%` }} />
      </div>
      <span className="num text-[11px] text-ink-500 tabular-nums w-7 text-right">{pct}%</span>
    </div>
  );
}

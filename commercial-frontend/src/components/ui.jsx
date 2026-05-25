import { Check, Sparkles } from 'lucide-react'

const TONES = [
  '#1a1a2e', '#16213e', '#0d1b2a', '#1b1f3b',
  '#1c1c1e', '#0f2027', '#1a1a1a', '#0d0d1a',
]

function toneFromId(id) {
  if (!id) return TONES[0]
  const str = String(id)
  let hash = 0
  for (let i = 0; i < str.length; i++) {
    hash = (hash * 31 + str.charCodeAt(i)) >>> 0
  }
  return TONES[hash % TONES.length]
}

export function Logo({ size = 28, className = '' }) {
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 32 32"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      className={className}
    >
      <rect width="32" height="32" rx="8" fill="#0f1117" />
      <rect x="7" y="8" width="11" height="16" rx="2" fill="#ffffff" opacity="0.9" />
      <rect x="14" y="8" width="11" height="16" rx="2" fill="#f59e0b" opacity="0.85" />
      <rect x="10.5" y="11" width="5" height="1.5" rx="0.75" fill="#0f1117" opacity="0.4" />
      <rect x="10.5" y="14" width="7" height="1.5" rx="0.75" fill="#0f1117" opacity="0.4" />
      <rect x="10.5" y="17" width="4" height="1.5" rx="0.75" fill="#0f1117" opacity="0.4" />
    </svg>
  )
}

export function Wordmark({ className = '' }) {
  return (
    <div className={`flex items-center gap-2 ${className}`}>
      <Logo size={28} />
      <div className="logo-wordmark">
        <span className="logo-text">TechFlow</span>
        <span className="logo-tagline">Gamer Hardware</span>
      </div>
    </div>
  )
}

const BADGE_STYLES = {
  neutral:  'bg-[#eeeef2] text-[#525461]',
  success:  'bg-emerald-50 text-emerald-700 border border-emerald-200',
  warn:     'bg-amber-50 text-amber-700 border border-amber-200',
  danger:   'bg-red-50 text-red-600 border border-red-200',
  ai:       'bg-amber-400/10 text-amber-600 border border-amber-300/30',
  invert:   'bg-[#16171d] text-white',
}

export function Badge({ children, tone = 'neutral', className = '' }) {
  return (
    <span className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-md text-[10px] font-semibold tracking-wide uppercase ${BADGE_STYLES[tone] ?? BADGE_STYLES.neutral} ${className}`}>
      {children}
    </span>
  )
}

export function CoverPlaceholder({ title = '', bookId, aiPick = false, className = '' }) {
  const tone = toneFromId(bookId)
  const initials = title
    .split(' ')
    .filter(Boolean)
    .slice(0, 2)
    .map((w) => w[0]?.toUpperCase() ?? '')
    .join('')

  return (
    <div
      className={`relative flex items-center justify-center w-full h-full select-none overflow-hidden ${className}`}
      style={{ background: tone }}
    >
      {/* diagonal stripe texture */}
      <svg
        className="absolute inset-0 w-full h-full opacity-[0.06]"
        xmlns="http://www.w3.org/2000/svg"
      >
        <defs>
          <pattern id={`stripe-${bookId}`} width="8" height="8" patternTransform="rotate(45)" patternUnits="userSpaceOnUse">
            <line x1="0" y1="0" x2="0" y2="8" stroke="white" strokeWidth="2" />
          </pattern>
        </defs>
        <rect width="100%" height="100%" fill={`url(#stripe-${bookId})`} />
      </svg>

      <span
        className="relative z-10 font-serif font-bold text-white/70 text-2xl leading-none tracking-tight"
      >
        {initials || '?'}
      </span>

      {aiPick && (
        <span className="absolute bottom-2 right-2 flex items-center gap-1 px-1.5 py-0.5 rounded-md bg-amber-400/20 border border-amber-400/30 text-amber-300 text-[9px] font-semibold">
          <Sparkles size={8} />
          IA
        </span>
      )}
    </div>
  )
}

export function Checkbox({ checked = false, onChange, label, className = '' }) {
  return (
    <label className={`flex items-center gap-2 cursor-pointer ${className}`}>
      <button
        type="button"
        role="checkbox"
        aria-checked={checked}
        onClick={() => onChange && onChange(!checked)}
        className={`
          flex-shrink-0 w-4 h-4 rounded border transition-all duration-150
          flex items-center justify-center
          ${checked
            ? 'bg-[#16171d] border-[#16171d]'
            : 'bg-white border-[#d9dae0] hover:border-[#8f92a1]'
          }
        `}
      >
        {checked && <Check size={10} strokeWidth={3} className="text-white" />}
      </button>
      {label && <span className="text-[13px] text-[#e0e9ff]">{label}</span>}
    </label>
  )
}

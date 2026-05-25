import { useState } from 'react'
import { useCartStore } from './cart.store'

/** @param {{ item: import('./cart.types').CartItem }} props */
export default function CartLine({ item }) {
  const updateQuantity = useCartStore((s) => s.updateQuantity)
  const removeItem = useCartStore((s) => s.removeItem)
  const [coverError, setCoverError] = useState(false)

  const lineTotal = (item.unitPrice * item.quantity).toLocaleString('es-CO', {
    style: 'currency',
    currency: 'COP',
    maximumFractionDigits: 0,
  })

  const unitFormatted = item.unitPrice.toLocaleString('es-CO', {
    style: 'currency',
    currency: 'COP',
    maximumFractionDigits: 0,
  })

  const initials = item.title
    .split(' ')
    .slice(0, 2)
    .map((w) => w[0])
    .join('')
    .toUpperCase()

  return (
    <div style={styles.row}>
      <div style={styles.cover}>
        {!coverError && item.coverUrl ? (
          <img
            src={item.coverUrl}
            alt={item.title}
            onError={() => setCoverError(true)}
            style={styles.coverImg}
          />
        ) : (
          <div style={styles.coverPlaceholder}>{initials}</div>
        )}
      </div>

      <div style={styles.info}>
        <p style={styles.title}>{item.title}</p>
        <div style={styles.priceRow}>
          <span style={styles.unitPrice}>{unitFormatted} c/u</span>
          {item.isPriceFallback && (
            <span style={styles.estimadoBadge}>Estimado</span>
          )}
        </div>
      </div>

      <div style={styles.controls}>
        <button
          style={styles.stepBtn}
          aria-label="Disminuir cantidad"
          onClick={() => updateQuantity(item.bookId, item.quantity - 1)}
        >
          −
        </button>
        <span style={styles.qty}>{item.quantity}</span>
        <button
          style={styles.stepBtn}
          aria-label="Aumentar cantidad"
          onClick={() => updateQuantity(item.bookId, item.quantity + 1)}
        >
          +
        </button>
      </div>

      <div style={styles.lineTotalWrap}>
        <span style={styles.lineTotal}>{lineTotal}</span>
        <button
          style={styles.removeBtn}
          aria-label="Eliminar del carrito"
          onClick={() => removeItem(item.bookId)}
        >
          ×
        </button>
      </div>
    </div>
  )
}

const styles = {
  row: {
    display: 'flex',
    alignItems: 'center',
    gap: '12px',
    padding: '12px 0',
    borderBottom: '1px solid var(--border)',
  },
  cover: {
    flexShrink: 0,
    width: 52,
    height: 68,
    borderRadius: 'var(--radius-sm)',
    overflow: 'hidden',
  },
  coverImg: {
    width: '100%',
    height: '100%',
    objectFit: 'cover',
  },
  coverPlaceholder: {
    width: '100%',
    height: '100%',
    background: 'var(--primary)',
    color: '#fff',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    fontSize: '14px',
    fontWeight: 700,
    letterSpacing: '0.05em',
  },
  info: {
    flex: 1,
    minWidth: 0,
  },
  title: {
    fontSize: '13px',
    fontWeight: 600,
    color: 'var(--text)',
    margin: 0,
    overflow: 'hidden',
    textOverflow: 'ellipsis',
    whiteSpace: 'nowrap',
  },
  priceRow: {
    display: 'flex',
    alignItems: 'center',
    gap: '6px',
    marginTop: '4px',
  },
  unitPrice: {
    fontSize: '12px',
    color: 'var(--text-muted)',
  },
  estimadoBadge: {
    fontSize: '10px',
    fontWeight: 600,
    color: '#92400E',
    background: '#FEF3C7',
    border: '1px solid #F59E0B',
    borderRadius: '4px',
    padding: '1px 5px',
    letterSpacing: '0.02em',
  },
  controls: {
    display: 'flex',
    alignItems: 'center',
    gap: '6px',
    flexShrink: 0,
  },
  stepBtn: {
    width: 28,
    height: 28,
    border: '1px solid var(--border)',
    borderRadius: 'var(--radius-sm)',
    background: 'var(--surface)',
    color: 'var(--text)',
    fontSize: '16px',
    lineHeight: 1,
    cursor: 'pointer',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    transition: 'var(--transition)',
  },
  qty: {
    minWidth: '20px',
    textAlign: 'center',
    fontSize: '14px',
    fontWeight: 600,
    color: 'var(--text)',
  },
  lineTotalWrap: {
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'flex-end',
    gap: '4px',
    flexShrink: 0,
  },
  lineTotal: {
    fontSize: '13px',
    fontWeight: 700,
    color: 'var(--primary)',
    whiteSpace: 'nowrap',
  },
  removeBtn: {
    background: 'none',
    border: 'none',
    cursor: 'pointer',
    color: 'var(--text-muted)',
    fontSize: '18px',
    lineHeight: 1,
    padding: '0 2px',
    transition: 'var(--transition)',
  },
}

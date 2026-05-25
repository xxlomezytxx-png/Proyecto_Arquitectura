import { useState, useCallback } from 'react'
import { useCartStore } from './cart.store'
import { selectHasItem } from './cart.selectors'

/**
 * @param {{
 *   product: {
 *     id: string|number,
 *     title: string,
 *     suggested_price?: number,
 *     price?: number,
 *     cover_url?: string,
 *     is_fallback?: boolean,
 *     isPriceFallback?: boolean,
 *   },
 *   disabled?: boolean,
 * }} props
 */
export default function AddToCartButton({ book, disabled = false }) {
  const productId = String(book.id)
  const hasItem = useCartStore(selectHasItem(productId))
  const addItem = useCartStore((s) => s.addItem)

  const [phase, setPhase] = useState('idle')

  const unitPrice = book.suggested_price ?? book.price ?? 0
  const isPriceFallback = book.isPriceFallback ?? book.is_fallback ?? false

  const handleAdd = useCallback(() => {
    if (hasItem || phase === 'adding' || disabled) return

    setPhase('adding')

    addItem({
      bookId: productId,
      title: book.title,
      quantity: 1,
      unitPrice,
      coverUrl: book.cover_url,
      isPriceFallback,
    })

    setTimeout(() => setPhase('idle'), 600)
  }, [hasItem, phase, disabled, addItem, productId, book, unitPrice, isPriceFallback])

  const inCart = hasItem

  if (inCart) {
    return (
      <button style={{ ...styles.base, ...styles.inCart }} disabled>
        <span style={styles.checkmark}>✓</span>
        En carrito
      </button>
    )
  }

  if (phase === 'adding') {
    return (
      <button style={{ ...styles.base, ...styles.adding }} disabled>
        <span style={styles.spinnerEl} />
        Agregando…
      </button>
    )
  }

  return (
    <button
      style={{
        ...styles.base,
        ...styles.idle,
        ...(disabled ? styles.disabledIdle : {}),
      }}
      onClick={handleAdd}
      disabled={disabled}
      aria-label={`Agregar ${book.title} al carrito`}
    >
      Agregar al carrito
    </button>
  )
}

const styles = {
  base: {
    display: 'inline-flex',
    alignItems: 'center',
    justifyContent: 'center',
    gap: '6px',
    width: '100%',
    padding: '10px 16px',
    borderRadius: 'var(--radius-md)',
    border: 'none',
    fontSize: '14px',
    fontWeight: 600,
    cursor: 'pointer',
    transition: 'var(--transition)',
    letterSpacing: '0.01em',
    whiteSpace: 'nowrap',
  },
  idle: {
    background: 'var(--primary)',
    color: '#fff',
  },
  disabledIdle: {
    background: 'var(--text-light)',
    cursor: 'not-allowed',
    opacity: 0.6,
  },
  adding: {
    background: 'var(--accent)',
    color: '#fff',
    opacity: 0.85,
    cursor: 'wait',
  },
  inCart: {
    background: 'var(--accent-light)',
    color: 'var(--accent)',
    cursor: 'default',
  },
  checkmark: {
    fontSize: '13px',
    fontWeight: 700,
  },
  spinnerEl: {
    display: 'inline-block',
    width: '12px',
    height: '12px',
    border: '2px solid rgba(255,255,255,0.4)',
    borderTopColor: '#fff',
    borderRadius: '50%',
    animation: 'cart-spin 0.7s linear infinite',
  },
}

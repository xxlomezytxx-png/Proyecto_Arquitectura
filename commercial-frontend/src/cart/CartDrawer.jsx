import { useState, useEffect } from 'react'
import { useCartStore } from './cart.store'
import {
  selectItems,
  selectTotalAmount,
  selectTotalItems,
} from './cart.selectors'
import CartLine from './CartLine'
import { createOrder } from '../services/orderService'
import { useAuthStore } from '../auth/authStore'
import CheckoutModal from '../checkout/CheckoutModal'
import OrderSuccessModal from '../checkout/OrderSuccessModal'
import { saveOrder } from '../orders/orders.storage'

/**
 * @param {{ isOpen: boolean, onClose: () => void }} props
 */
export default function CartDrawer({ isOpen, onClose }) {
  const items = useCartStore(selectItems)

  const totalAmount = useCartStore(selectTotalAmount)

  const totalItems = useCartStore(selectTotalItems)

  const clear = useCartStore((s) => s.clear)

  const { user } = useAuthStore()

  const [orderState, setOrderState] = useState('idle')

  const [checkoutOpen, setCheckoutOpen] = useState(false)

  const [successOpen, setSuccessOpen] = useState(false)

  const [successData, setSuccessData] = useState(null)

  const [toastVisible, setToastVisible] = useState(false)

  useEffect(() => {
    if (!isOpen) return

    const onKey = (e) => {
      if (e.key === 'Escape') onClose()
    }

    document.addEventListener('keydown', onKey)

    return () => {
      document.removeEventListener('keydown', onKey)
    }
  }, [isOpen, onClose])

  useEffect(() => {
    document.body.style.overflow = isOpen ? 'hidden' : ''

    return () => {
      document.body.style.overflow = ''
    }
  }, [isOpen])

  async function handleConfirm(checkoutData) {
    if (orderState === 'loading' || items.length === 0) {
      return
    }

    const invalidItems = items.filter((item) => item.isFallback === true || item.is_fallback === true || String(item.bookId).startsWith('fallback-'))
    if (invalidItems.length > 0) {
      setOrderState('error-invalid')
      setTimeout(() => setOrderState('idle'), 3000)
      return
    }

    setOrderState('loading')

    const customerId =
      user?.id ??
      ('guest-' + (crypto.randomUUID?.() ?? 'anon'))

    const subtotal = items.reduce(
      (sum, item) =>
        sum + (item.unitPrice ?? 0) * item.quantity,
      0
    )
    const taxes = Math.round(subtotal * 0.12)
    const total = subtotal + taxes
    const orderId = `ORD-${Math.floor(
      Math.random() * 90000 + 10000
    )}`

    const invoice = {
      id: orderId,
      customer: {
        name: checkoutData.fullName,
        email: checkoutData.email,
        address: checkoutData.address,
        city: checkoutData.city,
        phone: checkoutData.phone,
      },
      products: items.map((item) => ({
        bookId: item.bookId,
        title: item.title,
        quantity: item.quantity,
        unitPrice: item.unitPrice,
      })),
      items,
      subtotal,
      taxes,
      total,
      paymentMethod: checkoutData.paymentMethod,
      createdAt: new Date().toISOString(),
      status: 'Completed',
    }

    try {
      await createOrder(customerId, items)

      const orderData = {
        ...invoice,
        orderNumber: orderId,
        date: new Date().toLocaleDateString('es-CO'),
        subtotalFormatted: subtotal.toLocaleString('es-CO', {
          style: 'currency',
          currency: 'COP',
          maximumFractionDigits: 0,
        }),
        taxesFormatted: taxes.toLocaleString('es-CO', {
          style: 'currency',
          currency: 'COP',
          maximumFractionDigits: 0,
        }),
        total: total.toLocaleString('es-CO', {
          style: 'currency',
          currency: 'COP',
          maximumFractionDigits: 0,
        }),
      }

      setSuccessData(orderData)
      saveOrder(orderData)
      setSuccessOpen(true)
      setToastVisible(true)
      setTimeout(() => setToastVisible(false), 3600)
      clear()
      setOrderState('done')

      setTimeout(() => {
        setOrderState('idle')
        onClose()
      }, 1500)
    } catch (error) {
      console.error(error)

      if (error.response?.status === 409) {
        setOrderState('stock-error')
      } else {
        setOrderState('error')
      }

      setTimeout(() => {
        setOrderState('idle')
      }, 3000)
    }
  }

  const totalFormatted =
    totalAmount.toLocaleString(
      'es-CO',
      {
        style: 'currency',
        currency: 'COP',
        maximumFractionDigits: 0,
      }
    )

  return (
    <>
      {isOpen && (
        <div
          className="cart-backdrop"
          aria-hidden="true"
          onClick={onClose}
        />
      )}

      <aside
        role="dialog"
        aria-modal="true"
        aria-label="Carrito de compras"
        className={`cart-drawer${
          isOpen ? ' is-open' : ''
        }`}
      >
        <div className="cart-drawer__header">
          <div>
            <h2 className="cart-drawer__title">
              TechFlow Carrito
            </h2>

            {totalItems > 0 && (
              <p className="cart-drawer__subtitle">
                {totalItems}{' '}
                {totalItems === 1
                  ? 'artículo'
                  : 'artículos'}
              </p>
            )}
          </div>

          <button
            className="cart-drawer__close"
            onClick={onClose}
            aria-label="Cerrar carrito"
          >
            ×
          </button>
        </div>

        <div className="cart-drawer__body">
          {items.length === 0 ? (
            <div className="cart-drawer__empty">
              <span className="cart-drawer__empty-icon">
                🛒
              </span>

              <p className="cart-drawer__empty-text">
                Tu carrito está vacío
              </p>

              <p className="cart-drawer__empty-hint">
                Agrega hardware premium de la tienda
              </p>
            </div>
          ) : (
            <div>
              {items.map((item) => (
                <CartLine
                  key={item.bookId}
                  item={item}
                />
              ))}
            </div>
          )}
        </div>

        {items.length > 0 && (
          <div className="cart-drawer__footer">
            <div className="cart-drawer__summary-row">
              <span className="cart-drawer__summary-label">
                Total estimado
              </span>

              <span className="cart-drawer__summary-amount">
                {totalFormatted}
              </span>
            </div>

            {orderState === 'error' && (
              <p className="cart-drawer__error">
                Error al crear el pedido.
                Intenta de nuevo.
              </p>
            )}

            {orderState === 'error-invalid' && (
              <p className="cart-drawer__error">
                Hay productos en el carrito que no están disponibles para la compra.
                Elimina los elementos marcados o recarga la página.
              </p>
            )}

            {orderState === 'stock-error' && (
              <p className="cart-drawer__error">
                Algunos productos ya no tienen
                stock disponible.
              </p>
            )}

            <button
              className="cart-drawer__cta"
              onClick={() =>
                setCheckoutOpen(true)
              }
              disabled={
                orderState === 'loading' || items.some((item) => item.isFallback === true || item.is_fallback === true || String(item.bookId).startsWith('fallback-'))
              }
            >
              Proceder al pago
            </button>
          </div>
        )}
      </aside>

      {toastVisible && (
        <div className="cart-toast">
          <strong>¡Pedido completado!</strong> Tu compra fue procesada correctamente.
        </div>
      )}

      <CheckoutModal
        isOpen={checkoutOpen}
        onClose={() =>
          setCheckoutOpen(false)
        }
        onConfirm={async (
          checkoutData
        ) => {
          setCheckoutOpen(false)

          await handleConfirm(
            checkoutData
          )
        }}
      />

      <OrderSuccessModal
        isOpen={successOpen}
        onClose={() =>
          setSuccessOpen(false)
        }
        orderData={successData}
      />
    </>
  )
}
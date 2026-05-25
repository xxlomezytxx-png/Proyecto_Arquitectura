import { useEffect, useState } from 'react'
import { useCartStore } from '../cart/cart.store'
import {
  selectItems,
  selectTotalAmount,
} from '../cart/cart.selectors'
import { useAuthStore } from '../auth/authStore'

export default function CheckoutModal({
  isOpen,
  onClose,
  onConfirm,
}) {
  const items = useCartStore(selectItems)
  const totalAmount = useCartStore(selectTotalAmount)

  const { user } = useAuthStore()

  const [form, setForm] = useState({
    fullName:
      user?.name ||
      user?.full_name ||
      user?.username ||
      '',

    email: user?.email || '',

    address: '',

    city: '',

    phone:
      user?.phone ||
      user?.telefono ||
      '',

    paymentMethod: 'PSE',
  })

  const [errors, setErrors] = useState({})

  useEffect(() => {
    if (isOpen) {
      setErrors({})
    }
  }, [isOpen])

  if (!isOpen) return null

  const totalFormatted = totalAmount.toLocaleString('es-CO', {
    style: 'currency',
    currency: 'COP',
    maximumFractionDigits: 0,
  })

  function handleChange(e) {
    setForm({
      ...form,
      [e.target.name]: e.target.value,
    })
  }

  function validate() {
    const nextErrors = {}

    if (!form.fullName.trim()) {
      nextErrors.fullName = 'Nombre completo es requerido.'
    }
    if (!form.email.trim()) {
      nextErrors.email = 'Email es requerido.'
    } else if (
      !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(form.email)
    ) {
      nextErrors.email = 'Email inválido.'
    }
    if (!form.address.trim()) {
      nextErrors.address = 'Dirección es requerida.'
    }
    if (!form.city.trim()) {
      nextErrors.city = 'Ciudad es requerida.'
    }
    if (!form.phone.trim()) {
      nextErrors.phone = 'Teléfono es requerido.'
    }

    return nextErrors
  }

  function handleSubmit() {
    const validation = validate()
    if (Object.keys(validation).length > 0) {
      setErrors(validation)
      return
    }

    onConfirm(form)
  }

  return (
    <div style={styles.overlay}>
      <div style={styles.modal}>
        <div style={styles.header}>
          <h2 style={styles.title}>
            Finalizar compra
          </h2>

          <button
            onClick={onClose}
            style={styles.closeBtn}
          >
            ×
          </button>
        </div>

        <div style={styles.body}>
          <div style={styles.section}>
            <h3 style={styles.sectionTitle}>
              Datos de entrega
            </h3>

            <input
              style={styles.input}
              name="fullName"
              placeholder="Nombre completo"
              value={form.fullName}
              onChange={handleChange}
            />
            {errors.fullName && (
              <span style={styles.error}>
                {errors.fullName}
              </span>
            )}

            <input
              style={styles.input}
              name="email"
              type="email"
              placeholder="Correo electrónico"
              value={form.email}
              onChange={handleChange}
            />
            {errors.email && (
              <span style={styles.error}>
                {errors.email}
              </span>
            )}

            <input
              style={styles.input}
              name="address"
              placeholder="Dirección"
              value={form.address}
              onChange={handleChange}
            />
            {errors.address && (
              <span style={styles.error}>
                {errors.address}
              </span>
            )}

            <input
              style={styles.input}
              name="city"
              placeholder="Ciudad"
              value={form.city}
              onChange={handleChange}
            />
            {errors.city && (
              <span style={styles.error}>
                {errors.city}
              </span>
            )}

            <input
              style={styles.input}
              name="phone"
              placeholder="Teléfono"
              value={form.phone}
              onChange={handleChange}
            />
            {errors.phone && (
              <span style={styles.error}>
                {errors.phone}
              </span>
            )}
          </div>

          <div style={styles.section}>
            <h3 style={styles.sectionTitle}>
              Método de pago
            </h3>

            <select
              style={styles.input}
              name="paymentMethod"
              value={form.paymentMethod}
              onChange={handleChange}
            >
              <option value="PSE">PSE</option>
              <option value="Tarjeta">
                Tarjeta
              </option>
              <option value="Contra entrega">
                Contra entrega
              </option>
            </select>
          </div>

          <div style={styles.section}>
            <h3 style={styles.sectionTitle}>
              Resumen del pedido
            </h3>

            {items.map((item) => (
              <div
                key={item.bookId}
                style={styles.item}
              >
                <div style={styles.itemInfo}>
                  <span style={styles.itemTitle}>
                    {item.title}
                  </span>

                  <span style={styles.itemQty}>
                    Cantidad: {item.quantity}
                  </span>
                </div>

                <span style={styles.itemPrice}>
                  {(item.unitPrice * item.quantity).toLocaleString(
                    'es-CO',
                    {
                      style: 'currency',
                      currency: 'COP',
                      maximumFractionDigits: 0,
                    }
                  )}
                </span>
              </div>
            ))}

            <div style={styles.total}>
              <span>Total</span>
              <span>{totalFormatted}</span>
            </div>
          </div>
        </div>

        <button
          style={styles.confirmBtn}
          onClick={handleSubmit}
        >
          Confirmar compra
        </button>
      </div>
    </div>
  )
}

const styles = {
  overlay: {
    position: 'fixed',
    inset: 0,
    background: 'rgba(0,0,0,0.55)',
    display: 'flex',
    justifyContent: 'center',
    alignItems: 'center',
    zIndex: 9999,
    padding: '20px',
  },

  modal: {
    width: '100%',
    maxWidth: '560px',
    maxHeight: '90vh',
    overflowY: 'auto',
    background: '#fff',
    borderRadius: '20px',
    padding: '28px',
    boxShadow: '0 20px 50px rgba(0,0,0,0.15)',
  },

  header: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: '24px',
  },

  title: {
    margin: 0,
    fontSize: '24px',
    fontWeight: 700,
    color: '#111827',
  },

  closeBtn: {
    border: 'none',
    background: '#F3F4F6',
    width: '36px',
    height: '36px',
    borderRadius: '50%',
    fontSize: '22px',
    cursor: 'pointer',
    color: '#374151',
  },

  body: {
    display: 'flex',
    flexDirection: 'column',
    gap: '28px',
  },

  section: {
    display: 'flex',
    flexDirection: 'column',
    gap: '12px',
  },

  sectionTitle: {
    margin: 0,
    fontSize: '18px',
    fontWeight: 600,
    color: '#111827',
  },

  input: {
    padding: '14px',
    borderRadius: '10px',
    border: '1px solid #D1D5DB',
    fontSize: '14px',
    outline: 'none',
  },

  item: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: '12px 0',
    borderBottom: '1px solid #E5E7EB',
  },

  itemInfo: {
    display: 'flex',
    flexDirection: 'column',
    gap: '4px',
  },

  itemTitle: {
    fontWeight: 600,
    color: '#111827',
  },

  itemQty: {
    fontSize: '13px',
    color: '#6B7280',
  },

  itemPrice: {
    fontWeight: 600,
    color: '#7C3AED',
  },

  total: {
    marginTop: '12px',
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    fontWeight: 700,
    fontSize: '20px',
    color: '#111827',
  },

  confirmBtn: {
    width: '100%',
    marginTop: '28px',
    padding: '16px',
    border: 'none',
    borderRadius: '12px',
    background: '#7C3AED',
    color: '#fff',
    fontWeight: 700,
    fontSize: '15px',
    cursor: 'pointer',
  },

  error: {
    color: '#dc2626',
    fontSize: '12px',
    marginTop: '6px',
    display: 'block',
  },
}
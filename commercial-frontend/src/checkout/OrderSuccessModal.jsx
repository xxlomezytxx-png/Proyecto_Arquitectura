import { generateInvoice } from '../orders/generateInvoice'

export default function OrderSuccessModal({
  isOpen,
  onClose,
  orderData,
}) {
  if (!isOpen || !orderData) return null

  return (
    <div style={styles.overlay}>
      <div style={styles.modal}>
        <div style={styles.icon}>
          ✓
        </div>

        <h2 style={styles.title}>
          ¡Compra realizada!
        </h2>

        <p style={styles.subtitle}>
          Tu pedido fue confirmado exitosamente
        </p>

        <div style={styles.section}>
          <div style={styles.row}>
            <span>Número pedido</span>

            <strong>
              {orderData.orderNumber}
            </strong>
          </div>

          <div style={styles.row}>
            <span>Fecha</span>

            <strong>
              {new Date(orderData.createdAt).toLocaleString('es-CO', {
                dateStyle: 'short',
                timeStyle: 'short',
              })}
            </strong>
          </div>

          <div style={styles.row}>
            <span>Estado</span>

            <strong>
              {orderData.status}
            </strong>
          </div>

          <div style={styles.row}>
            <span>Cliente</span>

            <strong>
              {orderData.customer?.name}
            </strong>
          </div>

          <div style={styles.row}>
            <span>Email</span>

            <strong>
              {orderData.customer?.email}
            </strong>
          </div>

          <div style={styles.row}>
            <span>Ciudad</span>

            <strong>
              {orderData.customer?.city}
            </strong>
          </div>

          <div style={styles.row}>
            <span>Dirección</span>

            <strong>
              {orderData.customer?.address}
            </strong>
          </div>

          <div style={styles.row}>
            <span>Pago</span>

            <strong>
              {orderData.paymentMethod}
            </strong>
          </div>
        </div>

        <div style={styles.products}>
          {orderData.items.map((item) => (
            <div
              key={item.bookId}
              style={styles.product}
            >
              <span>
                {item.title} x{item.quantity}
              </span>

              <strong>
                {(item.unitPrice *
                  item.quantity).toLocaleString(
                  'es-CO',
                  {
                    style: 'currency',
                    currency: 'COP',
                    maximumFractionDigits: 0,
                  }
                )}
              </strong>
            </div>
          ))}
        </div>

        <div style={styles.total}>
          Total pagado:
          {' '}
          {orderData.total}
        </div>

        <div style={styles.actions}>
          <button
            style={styles.pdfButton}
            onClick={() =>
              generateInvoice(orderData)
            }
          >
            Descargar factura PDF
          </button>

          <button
            style={styles.button}
            onClick={onClose}
          >
            Continuar
          </button>
        </div>
      </div>
    </div>
  )
}

const styles = {
  overlay: {
    position: 'fixed',
    inset: 0,
    background: 'radial-gradient(circle at top, rgba(124, 58, 237, 0.22), transparent 30%), rgba(0,0,0,0.72)',
    display: 'flex',
    justifyContent: 'center',
    alignItems: 'center',
    zIndex: 99999,
    padding: '20px',
  },

  modal: {
    width: '100%',
    maxWidth: '600px',
    background: '#0f172a',
    borderRadius: '24px',
    padding: '32px',
    maxHeight: '90vh',
    overflowY: 'auto',
    color: '#f8fafc',
    boxShadow: '0 25px 80px rgba(124, 58, 237, 0.35)',
    border: '1px solid rgba(124, 58, 237, 0.35)',
  },

  icon: {
    width: '80px',
    height: '80px',
    borderRadius: '50%',
    background: '#DCFCE7',
    color: '#16A34A',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    fontSize: '42px',
    margin: '0 auto 20px',
    fontWeight: 'bold',
  },

  title: {
    textAlign: 'center',
    marginBottom: '8px',
    fontSize: '30px',
  },

  subtitle: {
    textAlign: 'center',
    color: '#6B7280',
    marginBottom: '28px',
    fontSize: '15px',
  },

  section: {
    background: '#F9FAFB',
    padding: '18px',
    borderRadius: '14px',
    display: 'flex',
    flexDirection: 'column',
    gap: '10px',
    marginBottom: '24px',
  },

  row: {
    display: 'flex',
    justifyContent: 'space-between',
    gap: '20px',
  },

  products: {
    display: 'flex',
    flexDirection: 'column',
    gap: '10px',
    marginBottom: '24px',
  },

  product: {
    display: 'flex',
    justifyContent: 'space-between',
    borderBottom: '1px solid #E5E7EB',
    paddingBottom: '10px',
    gap: '20px',
  },

  total: {
    fontSize: '22px',
    fontWeight: 'bold',
    textAlign: 'right',
    marginBottom: '24px',
    color: '#7C3AED',
  },

  actions: {
    display: 'flex',
    flexDirection: 'column',
    gap: '12px',
  },

  pdfButton: {
    width: '100%',
    padding: '16px',
    border: '2px solid rgba(124, 58, 237, 0.9)',
    borderRadius: '12px',
    background: 'rgba(17, 24, 39, 0.95)',
    color: '#ddd6fe',
    fontWeight: 'bold',
    cursor: 'pointer',
    fontSize: '15px',
  },

  button: {
    width: '100%',
    padding: '16px',
    border: 'none',
    borderRadius: '12px',
    background: 'linear-gradient(135deg, #7C3AED, #4F46E5)',
    color: '#fff',
    fontWeight: 'bold',
    cursor: 'pointer',
    fontSize: '15px',
  },
}
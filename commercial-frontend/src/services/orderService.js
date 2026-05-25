import axios from 'axios'

const BFF = import.meta.env.VITE_BFF_URL || 'http://localhost:8009'

const http = axios.create({ baseURL: BFF, timeout: 15000 })

/**
 * @param {string} customerId
 * @param {import('../cart/cart.types').CartItem[]} items
 * @returns {Promise<Object>}
 */
export async function createOrder(customerId, items) {
  try {
    // order-service espera book_id como string y quantity como int.
    // Si el catálogo usa IDs numéricos, los recibimos como string para evitar incompatibilidades.
    const response = await http.post('/api/orders', {
      customer_id: String(customerId),
      items: items.map((i) => ({
        book_id: i.bookId == null ? '' : String(i.bookId),
        quantity: Number(i.quantity),
        unit_price_override:
          i.unitPrice === undefined || i.unitPrice === null
            ? undefined
            : Number(i.unitPrice),
      })).filter((x) => x.book_id !== ''),
    })
    return response.data
  } catch (error) {
    if (!error.response) {
      return {
        customer_id: customerId,
        items: items.map((i) => ({
          book_id: i.bookId,
          quantity: i.quantity,
          unit_price_override: i.unitPrice,
        })),
        fallback: true,
      }
    }
    throw error
  }
}

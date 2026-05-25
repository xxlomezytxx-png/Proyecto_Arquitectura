import { create } from 'zustand'
import { persist } from 'zustand/middleware'

/**
 * @returns {import('./cart.types').CartState}
 */
export const useCartStore = create(
  persist(
    (set, get) => ({
      items: [],

      addItem: (item) => {
        const items = get().items
        const existing = items.find((i) => i.bookId === item.bookId)
        if (existing) {
          set({
            items: items.map((i) =>
              i.bookId === item.bookId
                ? { ...i, quantity: i.quantity + 1 }
                : i
            ),
          })
        } else {
          set({ items: [...items, { ...item, quantity: item.quantity ?? 1 }] })
        }
      },

      removeItem: (bookId) => {
        set({ items: get().items.filter((i) => i.bookId !== bookId) })
      },

      updateQuantity: (bookId, quantity) => {
        if (quantity <= 0) {
          set({ items: get().items.filter((i) => i.bookId !== bookId) })
        } else {
          set({
            items: get().items.map((i) =>
              i.bookId === bookId ? { ...i, quantity } : i
            ),
          })
        }
      },

      setUnitPrice: (bookId, unitPrice) => {
        set({
          items: get().items.map((i) =>
            i.bookId === bookId ? { ...i, unitPrice } : i
          ),
        })
      },

      clear: () => set({ items: [] }),
    }),
    { name: 'techflow-cart' }
  )
)

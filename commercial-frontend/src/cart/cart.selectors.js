/** @param {import('./cart.types').CartState} state */
export const selectItems = (state) => state.items

/** @param {import('./cart.types').CartState} state */
export const selectTotalItems = (state) =>
  state.items.reduce((sum, i) => sum + i.quantity, 0)

/** @param {import('./cart.types').CartState} state */
export const selectTotalAmount = (state) =>
  Math.round(
    state.items.reduce((sum, i) => sum + i.unitPrice * i.quantity, 0) * 100
  ) / 100

/** @param {string} bookId */
export const selectHasItem = (bookId) =>
  /** @param {import('./cart.types').CartState} state */
  (state) => state.items.some((i) => i.bookId === bookId)

/** @param {string} bookId */
export const selectQuantity = (bookId) =>
  /** @param {import('./cart.types').CartState} state */
  (state) => {
    const item = state.items.find((i) => i.bookId === bookId)
    return item ? item.quantity : 0
  }

/**
 * @typedef {Object} CartItem
 * @property {string} bookId
 * @property {string} title
 * @property {number} quantity
 * @property {number} unitPrice
 * @property {string} [coverUrl]
 * @property {boolean} [isPriceFallback]
 */

/**
 * @typedef {Object} CartState
 * @property {CartItem[]} items
 * @property {(item: CartItem) => void} addItem
 * @property {(bookId: string) => void} removeItem
 * @property {(bookId: string, quantity: number) => void} updateQuantity
 * @property {(bookId: string, unitPrice: number) => void} setUnitPrice
 * @property {() => void} clear
 */

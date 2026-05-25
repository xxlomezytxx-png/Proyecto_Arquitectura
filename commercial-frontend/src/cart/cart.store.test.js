import { describe, it, expect, beforeEach } from 'vitest'
import { useCartStore } from './cart.store'

const BOOK_A = { bookId: 'b1', title: 'Clean Code', quantity: 1, unitPrice: 12.5 }
const BOOK_B = { bookId: 'b2', title: 'DDD', quantity: 1, unitPrice: 20.0 }

beforeEach(() => {
  localStorage.clear()
  useCartStore.setState({ items: [] })
})

describe('addItem', () => {
  it('adds a new item to empty cart', () => {
    useCartStore.getState().addItem(BOOK_A)
    const { items } = useCartStore.getState()
    expect(items).toHaveLength(1)
    expect(items[0].bookId).toBe('b1')
    expect(items[0].quantity).toBe(1)
  })

  it('increments quantity when same book added twice', () => {
    useCartStore.getState().addItem(BOOK_A)
    useCartStore.getState().addItem(BOOK_A)
    const { items } = useCartStore.getState()
    expect(items).toHaveLength(1)
    expect(items[0].quantity).toBe(2)
  })

  it('adds distinct books as separate items', () => {
    useCartStore.getState().addItem(BOOK_A)
    useCartStore.getState().addItem(BOOK_B)
    expect(useCartStore.getState().items).toHaveLength(2)
  })

  it('defaults quantity to 1 when not specified', () => {
    const { quantity: _, ...noQty } = BOOK_A
    useCartStore.getState().addItem(noQty)
    expect(useCartStore.getState().items[0].quantity).toBe(1)
  })

  it('preserves isPriceFallback flag', () => {
    useCartStore.getState().addItem({ ...BOOK_A, isPriceFallback: true })
    expect(useCartStore.getState().items[0].isPriceFallback).toBe(true)
  })
})

describe('removeItem', () => {
  it('removes the matching book', () => {
    useCartStore.getState().addItem(BOOK_A)
    useCartStore.getState().addItem(BOOK_B)
    useCartStore.getState().removeItem('b1')
    const { items } = useCartStore.getState()
    expect(items).toHaveLength(1)
    expect(items[0].bookId).toBe('b2')
  })

  it('no-ops when book not in cart', () => {
    useCartStore.getState().addItem(BOOK_A)
    useCartStore.getState().removeItem('unknown')
    expect(useCartStore.getState().items).toHaveLength(1)
  })
})

describe('updateQuantity', () => {
  it('sets the quantity of an existing item', () => {
    useCartStore.getState().addItem(BOOK_A)
    useCartStore.getState().updateQuantity('b1', 5)
    expect(useCartStore.getState().items[0].quantity).toBe(5)
  })

  it('removes item when quantity set to 0', () => {
    useCartStore.getState().addItem(BOOK_A)
    useCartStore.getState().updateQuantity('b1', 0)
    expect(useCartStore.getState().items).toHaveLength(0)
  })

  it('removes item when quantity is negative', () => {
    useCartStore.getState().addItem(BOOK_A)
    useCartStore.getState().updateQuantity('b1', -1)
    expect(useCartStore.getState().items).toHaveLength(0)
  })
})

describe('setUnitPrice', () => {
  it('updates unit price of matching item', () => {
    useCartStore.getState().addItem(BOOK_A)
    useCartStore.getState().setUnitPrice('b1', 9.99)
    expect(useCartStore.getState().items[0].unitPrice).toBe(9.99)
  })

  it('does not affect other items', () => {
    useCartStore.getState().addItem(BOOK_A)
    useCartStore.getState().addItem(BOOK_B)
    useCartStore.getState().setUnitPrice('b1', 5.0)
    expect(useCartStore.getState().items[1].unitPrice).toBe(20.0)
  })
})

describe('clear', () => {
  it('empties the cart', () => {
    useCartStore.getState().addItem(BOOK_A)
    useCartStore.getState().addItem(BOOK_B)
    useCartStore.getState().clear()
    expect(useCartStore.getState().items).toHaveLength(0)
  })
})

describe('immutability', () => {
  it('does not mutate previous state reference', () => {
    useCartStore.getState().addItem(BOOK_A)
    const before = useCartStore.getState().items
    useCartStore.getState().addItem(BOOK_B)
    const after = useCartStore.getState().items
    expect(before).not.toBe(after)
  })
})

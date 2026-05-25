import { describe, it, expect } from 'vitest'
import {
  selectItems,
  selectTotalItems,
  selectTotalAmount,
  selectHasItem,
  selectQuantity,
} from './cart.selectors'

const makeState = (items) => ({ items })

const ITEM_A = { bookId: 'b1', title: 'Clean Code', quantity: 2, unitPrice: 12.5 }
const ITEM_B = { bookId: 'b2', title: 'DDD', quantity: 1, unitPrice: 20.0 }

describe('selectItems', () => {
  it('returns the items array', () => {
    const state = makeState([ITEM_A])
    expect(selectItems(state)).toBe(state.items)
  })
})

describe('selectTotalItems', () => {
  it('returns 0 for empty cart', () => {
    expect(selectTotalItems(makeState([]))).toBe(0)
  })

  it('sums quantities across multiple items', () => {
    expect(selectTotalItems(makeState([ITEM_A, ITEM_B]))).toBe(3)
  })

  it('counts single item quantity correctly', () => {
    expect(selectTotalItems(makeState([ITEM_A]))).toBe(2)
  })
})

describe('selectTotalAmount', () => {
  it('returns 0 for empty cart', () => {
    expect(selectTotalAmount(makeState([]))).toBe(0)
  })

  it('calculates total for single item', () => {
    expect(selectTotalAmount(makeState([ITEM_A]))).toBe(25.0)
  })

  it('calculates total across multiple items', () => {
    expect(selectTotalAmount(makeState([ITEM_A, ITEM_B]))).toBe(45.0)
  })

  it('rounds floating-point total to 2 decimal places', () => {
    const item = { bookId: 'b3', quantity: 3, unitPrice: 0.1 }
    expect(selectTotalAmount(makeState([item]))).toBe(0.3)
  })
})

describe('selectHasItem', () => {
  it('returns true when book is in cart', () => {
    expect(selectHasItem('b1')(makeState([ITEM_A]))).toBe(true)
  })

  it('returns false when book is not in cart', () => {
    expect(selectHasItem('b99')(makeState([ITEM_A]))).toBe(false)
  })

  it('returns false for empty cart', () => {
    expect(selectHasItem('b1')(makeState([]))).toBe(false)
  })
})

describe('selectQuantity', () => {
  it('returns quantity for existing item', () => {
    expect(selectQuantity('b1')(makeState([ITEM_A]))).toBe(2)
  })

  it('returns 0 when item not in cart', () => {
    expect(selectQuantity('b99')(makeState([ITEM_A]))).toBe(0)
  })

  it('returns 0 for empty cart', () => {
    expect(selectQuantity('b1')(makeState([]))).toBe(0)
  })
})

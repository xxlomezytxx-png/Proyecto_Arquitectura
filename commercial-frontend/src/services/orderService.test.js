import { describe, it, expect, vi, beforeEach } from 'vitest'

const mockPost = vi.hoisted(() => vi.fn())

vi.mock('axios', () => ({
  default: {
    create: () => ({ post: mockPost }),
  },
}))

const { createOrder } = await import('./orderService')

const ITEMS = [
  { bookId: 'b1', title: 'Clean Code', quantity: 2, unitPrice: 12.5 },
  { bookId: 'b2', title: 'DDD', quantity: 1, unitPrice: 20.0 },
]

beforeEach(() => {
  vi.clearAllMocks()
})

describe('createOrder', () => {
  it('posts to /api/orders with correct snake_case payload', async () => {
    mockPost.mockResolvedValue({ data: { order_id: 'o1' } })

    await createOrder('cust-1', ITEMS)

    expect(mockPost).toHaveBeenCalledWith('/api/orders', {
      customer_id: 'cust-1',
      items: [
        { book_id: 'b1', quantity: 2, unit_price_override: 12.5 },
        { book_id: 'b2', quantity: 1, unit_price_override: 20.0 },
      ],
    })
  })

  it('returns response.data on success', async () => {
    const payload = { order_id: 'o1', status: 'created' }
    mockPost.mockResolvedValue({ data: payload })

    const result = await createOrder('cust-1', ITEMS)

    expect(result).toEqual(payload)
  })

  it('returns fallback data when backend is offline', async () => {
    mockPost.mockRejectedValue(new Error('Network Error'))

    const result = await createOrder('cust-1', ITEMS)

    expect(result).toEqual({
      customer_id: 'cust-1',
      items: [
        { book_id: 'b1', quantity: 2, unit_price_override: 12.5 },
        { book_id: 'b2', quantity: 1, unit_price_override: 20.0 },
      ],
      fallback: true,
    })
  })

  it('propagates HTTP errors with response object', async () => {
    const responseError = new Error('Conflict')
    responseError.response = { status: 409 }
    mockPost.mockRejectedValue(responseError)

    await expect(createOrder('cust-1', ITEMS)).rejects.toThrow('Conflict')
  })

  it('maps empty items array correctly', async () => {
    mockPost.mockResolvedValue({ data: { order_id: 'o2' } })

    await createOrder('cust-2', [])

    expect(mockPost).toHaveBeenCalledWith('/api/orders', {
      customer_id: 'cust-2',
      items: [],
    })
  })
})

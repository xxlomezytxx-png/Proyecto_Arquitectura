import axios from 'axios'

const BFF = import.meta.env.VITE_BFF_URL || 'http://localhost:8009'
const FETCH_LIMIT = 500

const http = axios.create({
  baseURL: BFF,
  timeout: 60000,
})

export async function getBooks(params = {}) {
  try {
    const response = await http.get('/api/catalog/products', {
      params: {
        ...params,
        limit: FETCH_LIMIT,
      },
    })

    const data = response.data

    if (Array.isArray(data)) {
      return { items: data, total: data.length }
    }

    if (data && Array.isArray(data.items)) {
      return data
    }

    if (data && Array.isArray(data.books)) {
      return { items: data.books, total: data.books.length }
    }

    return { items: [], total: 0 }
  } catch (error) {
    console.error('Error getBooks:', error)
    return { items: [], total: 0, _error: true }
  }
}

export async function searchBooks(q, params = {}) {
  try {
    const response = await http.get('/api/catalog/products', {
      params: {
        ...params,
        q,
        limit: FETCH_LIMIT,
      },
    })

    const data = response.data

    if (Array.isArray(data)) {
      return { items: data, total: data.length }
    }

    if (data && Array.isArray(data.items)) {
      return data
    }

    if (data && Array.isArray(data.books)) {
      return { items: data.books, total: data.books.length }
    }

    return { items: [], total: 0 }
  } catch (error) {
    console.error('Error searchBooks:', error)
    return { items: [], total: 0, _error: true }
  }
}

export async function getBook(id) {
  try {
    const response = await http.get(`/api/catalog/products/${id}`)
    const data = response.data

    if (Array.isArray(data)) {
      return data[0] || null
    }

    return data
  } catch (error) {
    console.error('Error getBook:', error)
    return null
  }
}

export async function getCategories() {
  try {
    const response = await http.get('/api/catalog/categories')
    return Array.isArray(response.data) ? response.data : []
  } catch (error) {
    console.error('Error getCategories:', error)
    return []
  }
}

export const getPlaceholderUrl = (title, hexColor = '2F6F52', size = '300x450') => {
  const cleanText = (title || 'Hardware')
    .normalize('NFD')
    .replace(/[\u0300-\u036f]/g, '')
    .replace(/[^a-zA-Z0-9\s]/g, '')
    .split(' ')
    .map((w) => w.charAt(0).toUpperCase() + w.slice(1).toLowerCase())
    .slice(0, 3)
    .join('+')

  return `https://placehold.co/${size}/${hexColor}/FFFFFF?text=${cleanText}&font=roboto`
}
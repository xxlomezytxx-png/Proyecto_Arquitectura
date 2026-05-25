const CART_KEY = 'techflow_cart'

export function getCart() {
  const raw = localStorage.getItem(CART_KEY)
  return raw ? JSON.parse(raw) : []
}

export function saveCart(cart) {
  localStorage.setItem(CART_KEY, JSON.stringify(cart))
  window.dispatchEvent(new Event('cart-updated'))
}

export function getStock(book) {
  if (book.stock === undefined || book.stock === null) return null
  return Number(book.stock)
}

export function addToCart(book) {
  const stock = getStock(book)

  if (stock !== null && stock <= 0) {
    alert('Este producto está agotado.')
    return getCart()
  }

  const cart = getCart()
  const existing = cart.find(item => Number(item.id) === Number(book.id))

  if (existing) {
    if (stock !== null && existing.quantity >= stock) {
      alert(`No puedes agregar más unidades. Stock disponible: ${stock}`)
      return cart
    }

    existing.quantity += 1
  } else {
    cart.push({
      id: book.id,
      title: book.title,
      author: book.author,
      price: book.price || book.suggested_price || null,
      cover_url: book.cover_url,
      stock: stock,
      quantity: 1
    })
  }

  saveCart(cart)
  alert('Producto agregado al carrito')
  return cart
}

export function removeFromCart(id) {
  const cart = getCart().filter(item => Number(item.id) !== Number(id))
  saveCart(cart)
  return cart
}

export function increaseQuantity(id) {
  const cart = getCart().map(item => {
    if (Number(item.id) === Number(id)) {
      if (item.stock !== null && item.stock !== undefined && item.quantity >= item.stock) {
        alert(`No puedes agregar más unidades. Stock disponible: ${item.stock}`)
        return item
      }

      return { ...item, quantity: item.quantity + 1 }
    }

    return item
  })

  saveCart(cart)
  return cart
}

export function decreaseQuantity(id) {
  const cart = getCart()
    .map(item => {
      if (Number(item.id) === Number(id)) {
        return { ...item, quantity: item.quantity - 1 }
      }

      return item
    })
    .filter(item => item.quantity > 0)

  saveCart(cart)
  return cart
}

export function getCartCount() {
  return getCart().reduce((total, item) => total + Number(item.quantity || 0), 0)
}

export function getCartTotal() {
  return getCart().reduce((total, item) => {
    const price = Number(item.price || 0)
    const quantity = Number(item.quantity || 0)
    return total + price * quantity
  }, 0)
}

export function clearCart() {
  localStorage.removeItem(CART_KEY)
  window.dispatchEvent(new Event('cart-updated'))
  return []
}

export function checkoutCart() {
  const cart = getCart()

  if (cart.length === 0) {
    alert('Tu carrito está vacío.')
    return []
  }

  clearCart()
  alert('Compra realizada exitosamente. Gracias por comprar en TechFlow.')
  return []
}
import { useEffect, useState } from 'react'
import {
  getCart,
  getCartTotal,
  increaseQuantity,
  decreaseQuantity,
  removeFromCart,
  clearCart,
  checkoutCart
} from '../cart'

export default function Cart() {
  const [items, setItems] = useState([])

  const refresh = () => {
    setItems(getCart())
    window.dispatchEvent(new Event('cart-updated'))
  }

  useEffect(() => {
    refresh()
  }, [])

  const handleIncrease = id => {
    increaseQuantity(id)
    refresh()
  }

  const handleDecrease = id => {
    decreaseQuantity(id)
    refresh()
  }

  const handleRemove = id => {
    removeFromCart(id)
    refresh()
  }

  const handleClear = () => {
    clearCart()
    refresh()
  }

  const handleCheckout = () => {
    checkoutCart()
    refresh()
  }

  return (
    <main className="cart-page">
      <h1>Carrito TechFlow</h1>

      {items.length === 0 && (
        <p className="empty">Tu carrito de hardware está vacío.</p>
      )}

      {items.length > 0 && (
        <>
          <div className="cart-list">
            {items.map(item => {
              const hasStock = item.stock !== null && item.stock !== undefined
              const reachedStock = hasStock && item.quantity >= item.stock

              return (
                <div className="cart-item" key={item.id}>
                  <img src={item.cover_url} alt={item.title} />

                  <div>
                    <h3>{item.title}</h3>
                    <p>{item.brand || item.author || 'Marca no disponible'}</p>

                    <p>
                      {item.price
                        ? `$${Number(item.price).toLocaleString('es-CO')}`
                        : 'Precio a consultar'}
                    </p>

                    {hasStock && (
                      <small>
                        Stock disponible: {item.stock} unidad(es)
                      </small>
                    )}

                    {reachedStock && (
                      <small className="stock-warning">
                        Ya agregaste el máximo disponible.
                      </small>
                    )}
                  </div>

                  <div className="cart-actions">
                    <button onClick={() => handleDecrease(item.id)}>-</button>
                    <strong>{item.quantity}</strong>
                    <button
                      onClick={() => handleIncrease(item.id)}
                      disabled={reachedStock}
                    >
                      +
                    </button>
                    <button onClick={() => handleRemove(item.id)}>
                      Eliminar
                    </button>
                  </div>
                </div>
              )
            })}
          </div>

          <div className="cart-summary">
            <strong>Total estimado del hardware:</strong>
            <span>
              {getCartTotal() > 0
                ? `$${Number(getCartTotal()).toLocaleString('es-CO')}`
                : 'Precio a consultar'}
            </span>
          </div>

          <div className="cart-footer-actions">
            <button className="checkout-button" onClick={handleCheckout}>
              Finalizar compra
            </button>

            <button className="clear-cart" onClick={handleClear}>
              Vaciar carrito
            </button>
          </div>
        </>
      )}
    </main>
  )
}
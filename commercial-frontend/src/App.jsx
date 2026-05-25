import { BrowserRouter, Routes, Route, Link } from 'react-router-dom'
import { useState, useEffect } from 'react'
import {
  Search,
  ShoppingCart,
  User,
  Truck,
  ShieldCheck,
  Sparkles,
  Package,
} from 'lucide-react'

import Catalogo from './pages/Catalogo'
import BookDetail from './components/BookDetail'
import IAPicks from './pages/IAPicks'
import OrdersPage from './orders/OrdersPage'

import CartDrawer from './cart/CartDrawer'

import FloatingChat from './components/FloatingChat'

import LoginModal from './auth/LoginModal'

import { Wordmark } from './components/ui'

import { useCartStore } from './cart/cart.store'
import { useAuthStore } from './auth/authStore'

import './index.css'

function Header({
  onSearchChange,
  onOpenCart,
  onOpenLogin,
}) {
  const [localSearch, setLocalSearch] =
    useState('')

  const items =
    useCartStore(
      (state) => state.items
    ) || []

  useEffect(() => {
    const timer = setTimeout(() => {
      onSearchChange(localSearch)
    }, 500)

    return () => clearTimeout(timer)
  }, [localSearch, onSearchChange])

  const count = items.reduce(
    (sum, item) =>
      sum + item.quantity,
    0
  )

  const { user, logout } =
    useAuthStore()

  return (
    <header className="store-header">
      <div className="header-utility-bar">
        <span className="header-utility-item">
          <Truck size={12} />
          Envío gratis en pedidos mayores a $50
        </span>

        <span className="header-utility-item">
          <ShieldCheck size={12} />
          Pago seguro garantizado
        </span>

        <span className="header-utility-item">
          <Sparkles size={12} />
          Recomendaciones impulsadas por IA
        </span>
      </div>

      <div className="header-inner">
        <Link
          to="/"
          className="header-logo"
        >
          <Wordmark />
        </Link>

        <nav className="header-nav">
          <Link
            to="/"
            className="nav-link"
          >
            Tienda
          </Link>

          <Link
            to="/ia-picks"
            className="nav-link nav-link-ai"
          >
            <Sparkles size={13} />
            Centro IA
          </Link>

          <Link
            to="/mis-pedidos"
            className="nav-link"
          >
            <Package size={13} />
            Pedidos
          </Link>
        </nav>

        <div className="search-wrap">
          <span className="search-icon">
            <Search size={15} />
          </span>

          <input
            className="search-input"
            type="text"
            placeholder="Busca PCs, GPUs, monitores o repuestos..."
            value={localSearch}
            onChange={(e) =>
              setLocalSearch(
                e.target.value
              )
            }
          />
        </div>

        <div className="header-actions">
          {user?.role === 'admin' && (
            <a
              href="http://localhost:3001"
              target="_blank"
              rel="noreferrer"
              className="header-admin-btn"
            >
              Panel Admin →
            </a>
          )}

          {user ? (
            <div className="user-menu">
              <span className="user-greeting">
                <User size={14} />
                {user.username}
              </span>

              <button
                onClick={logout}
                className="logout-btn"
              >
                Salir
              </button>
            </div>
          ) : (
            <button
              onClick={onOpenLogin}
              className="login-btn"
            >
              Iniciar sesión
            </button>
          )}

          <button
            onClick={onOpenCart}
            className="cart-btn"
            aria-label="Carrito"
          >
            <ShoppingCart size={19} />

            {count > 0 && (
              <span className="cart-badge">
                {count}
              </span>
            )}
          </button>
        </div>
      </div>
    </header>
  )
}

export default function App() {
  const [searchQuery, setSearchQuery] =
    useState('')

  const [isCartOpen, setIsCartOpen] =
    useState(false)

  const [isLoginOpen, setIsLoginOpen] =
    useState(false)

  return (
    <BrowserRouter>
      <Header
        onSearchChange={setSearchQuery}
        onOpenCart={() =>
          setIsCartOpen(true)
        }
        onOpenLogin={() =>
          setIsLoginOpen(true)
        }
      />

      <Routes>
        <Route
          path="/"
          element={
            <Catalogo
              searchQuery={searchQuery}
            />
          }
        />

        <Route
          path="/tienda"
          element={
            <Catalogo
              searchQuery={searchQuery}
            />
          }
        />

        <Route
          path="/catalogo"
          element={
            <Catalogo
              searchQuery={searchQuery}
            />
          }
        />

        <Route
          path="/producto/:id"
          element={<BookDetail />}
        />
        
        <Route
          path="/libro/:id"
          element={<BookDetail />}
        />

        <Route
          path="/ia-picks"
          element={<IAPicks />}
        />

        <Route
          path="/mis-pedidos"
          element={<OrdersPage />}
        />
      </Routes>

      <CartDrawer
        isOpen={isCartOpen}
        onClose={() =>
          setIsCartOpen(false)
        }
      />

      <FloatingChat />

      {isLoginOpen && (
        <LoginModal
          onClose={() =>
            setIsLoginOpen(false)
          }
        />
      )}
    </BrowserRouter>
  )
}
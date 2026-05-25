import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Heart, ShoppingCart, Check } from 'lucide-react'
import EnrichedBookImage from './EnrichedBookImage'
import { useCartStore } from '../cart/cart.store'
const formatCOP = (value) =>
  new Intl.NumberFormat('es-CO', {
    style: 'currency',
    currency: 'COP',
    maximumFractionDigits: 0,
  }).format(Number(value || 0))

const CONDITION_CLASSES = {
  nuevo: 'product-condition-nuevo',
  bueno: 'product-condition-bueno',
  aceptable: 'product-condition-aceptable',
  deteriorado: 'product-condition-deteriorado',
}

function getStock(product) {
  return product.stock ?? product.available_units ?? product.unidades_disponibles ?? product.units_available ?? null
}

function getCondition(product) {
  return product.condition ?? product.estado ?? product.estado_libro ?? product.book_condition ?? null
}

export default function ProductCard({ book: product, categories }) {
  const navigate = useNavigate()

  const [liked, setLiked] = useState(false)

  const items = useCartStore(s => s.items) || []
  const addItem = useCartStore(s => s.addItem)
  const removeItem = useCartStore(s => s.removeItem)

  const productIdStr = String(product.id)
  const inCart = items.some(i => i.bookId === productIdStr)
  const isFallbackProduct = product.isFallback === true || product.is_fallback === true

  const stock = getStock(product)
  const conditionRaw = getCondition(product)
  const conditionKey = conditionRaw ? String(conditionRaw).toLowerCase() : null
  const conditionClass = conditionKey ? (CONDITION_CLASSES[conditionKey] ?? 'product-condition-default') : null

  const price = product.price ?? product.suggested_price ?? null
  const year = product.publication_year ?? product.year ?? product.año ?? null

  const category = categories?.find(c => Number(c.id) === Number(product.category_id))

  const inStock =
    stock === null ||
    stock === undefined ||
    stock === '' ||
    Number(stock) > 0

  function handleCart(e) {
    e.stopPropagation()
    if (!inStock || isFallbackProduct) return
    if (inCart) {
      removeItem(productIdStr)
    } else {
      addItem({ bookId: productIdStr, ...product, unitPrice: product.price ?? product.suggested_price ?? 0, quantity: 1 })
    }
  }

  function handleHeart(e) {
    e.stopPropagation()
    setLiked(v => !v)
  }

  return (
    <div
      className="product-card"
      onClick={() => inStock && navigate(`/producto/${product.id}`)}
      style={{ cursor: inStock ? 'pointer' : 'default', opacity: inStock ? 1 : 0.6 }}
    >
      <div className="product-card-cover" style={{ position: 'relative' }}>
        <EnrichedBookImage book={product} height="100%" borderRadius="0" />

        {category && (
          <span className="product-card-cat">{category.name}</span>
        )}

        {!inStock && (
          <span className="product-card-soldout">Agotado</span>
        )}

        <button
          className="product-card-heart"
          onClick={handleHeart}
          aria-label={liked ? 'Remove from favorites' : 'Add to favorites'}
          style={{ color: liked ? '#06b6d4' : undefined }}
        >
          <Heart size={16} fill={liked ? '#06b6d4' : 'none'} />
        </button>

        <div
          aria-hidden="true"
          style={{
            position: 'absolute',
            inset: 0,
            background:
              'radial-gradient(circle at 20% 10%, rgba(6,182,212,0.18) 0%, transparent 45%), radial-gradient(circle at 80% 0%, rgba(59,130,246,0.12) 0%, transparent 45%)',
            pointerEvents: 'none',
          }}
        />
      </div>


      <div className="product-card-body">
        <h3 className="product-card-title">{product.title}</h3>
        <p className="product-card-author">Brand: {product.brand || product.manufacturer || product.author || 'Unknown Brand'}</p>

        <div className="product-card-meta">
          {stock !== null && stock !== undefined ? (
            <span>{stock > 0 ? `${stock} unidades en stock` : 'Agotado'}</span>
          ) : (
            <span>Stock variable</span>
          )}
          {year && (
            <><span className="product-card-meta-dot" /> <span>Release {year}</span></>
          )}
        </div>

        {conditionClass && (
          <span className={`product-condition-badge ${conditionClass}`}>
            {conditionRaw}
          </span>
        )}
      </div>


      <div className="product-card-footer">
        <div className="product-card-price-wrap">
        {price !== null && price !== undefined ? (
            <span className="product-card-price">{formatCOP(price)}</span>
          ) : (
            <>
              <span className="product-card-price-na">Precio a consultar</span>
              <span className={`price-source-badge ${product.is_fallback ? 'badge-estimado' : 'badge-verificado'}`}>
                {product.is_fallback ? 'Estimado' : 'Verificado'}
              </span>
            </>
          )}
        </div>

        <button
          className={`product-card-add${inCart ? ' remove' : ''}`}
          onClick={handleCart}
          disabled={!inStock || isFallbackProduct}
          aria-label={inCart ? 'Quitar del carrito' : isFallbackProduct ? 'Producto no disponible' : 'Agregar al carrito'}
        >
          {inCart ? <Check size={16} /> : <ShoppingCart size={16} />}
        </button>

      </div>
    </div>
  )
}

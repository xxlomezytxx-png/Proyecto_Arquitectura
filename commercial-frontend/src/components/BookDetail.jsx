import { useEffect, useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { getBook, getCategories } from '../api'
import EnrichedBookImage from './EnrichedBookImage'
import PriceBadge from './PriceBadge'
import AvailabilityBadge from './AvailabilityBadge'
import { useCartStore } from '../cart/cart.store'
import RecommendedBooks from './RecommendedBooks'
import { HARDWARE_PRODUCTS, HARDWARE_CATEGORIES } from '../hardwareMock'

function getStock(product) {
  return product.stock ?? product.available_units ?? product.unidades_disponibles ?? product.units_available ?? null
}

function getCondition(product) {
  return product.condition ?? product.estado ?? product.estado_libro ?? product.book_condition ?? null
}

export default function ProductDetail() {
  const { id } = useParams()
  const navigate = useNavigate()

  const [product, setProduct] = useState(null)
  const [categories, setCategories] = useState([])
  const [loading, setLoading] = useState(true)

  const addItem = useCartStore(s => s.addItem)
  const cartItem = useCartStore(s => s.items.find(i => i.bookId === String(id)))
  const cartQuantity = cartItem?.quantity || 0

  const [isLocalFallback, setIsLocalFallback] = useState(false)

  useEffect(() => {
    async function load() {
      setLoading(true)

      const [productData, categoriesData] = await Promise.all([
        getBook(id),
        getCategories(),
      ])

      const requestedId = String(id)
      const localHardware = !productData
        ? HARDWARE_PRODUCTS.find((item) => String(item.id) === requestedId.replace(/^fallback-/, ''))
        : null
      const resolvedProduct = productData || (localHardware ? {
        ...localHardware,
        id: `fallback-${localHardware.id}`,
        isFallback: true,
        is_fallback: true,
      } : null)

      setProduct(resolvedProduct)
      setCategories(
        productData
          ? categoriesData || []
          : localHardware
            ? HARDWARE_CATEGORIES
            : categoriesData || []
      )
      setIsLocalFallback(Boolean(localHardware))
      setLoading(false)
    }

    load()
  }, [id])

  if (loading) {
    return <main className="product-detail-page"><p>Cargando producto...</p></main>
  }

  if (!product) {
    return <main className="product-detail-page"><p>Producto no encontrado.</p></main>
  }

  const category = categories.find(c => Number(c.id) === Number(product.category_id))
  const stock = getStock(product)
  const condition = getCondition(product)
  const model = product.model || product.part_number || product.sku || product.isbn || product.book_reference || null

  const numericStock =
    stock === null || stock === undefined || stock === '' ? null : Number(stock)

  const isAvailable =
    numericStock === null || numericStock > 0

  const reachedStock =
    numericStock !== null && cartQuantity >= numericStock

  const handleAdd = () => {
    addItem({
      bookId: String(product.id),
      title: product.title,
      quantity: 1,
      unitPrice: product.suggested_price ?? product.price ?? 0,
      coverUrl: product.cover_url,
      isPriceFallback: product.is_fallback ?? false,
      isFallback: product.isFallback === true || product.is_fallback === true,
    })
  }

  return (
    <main className="product-detail-page">
      <button className="product-detail-back" onClick={() => navigate('/')}>
        ← Volver a la tienda
      </button>

      <section className="product-detail-grid">
        <div className="product-detail-cover">
          <EnrichedBookImage book={product} height="100%" />
        </div>

        <div className="product-detail-info">
          <span className="product-detail-category">
            {category?.name || 'Uncategorized'}
          </span>

          <h1 className="product-detail-title">{product.title}</h1>

          <p className="product-detail-author">
            Marca: <strong>{product.brand || product.manufacturer || product.author || 'Marca desconocida'}</strong>
          </p>

          <PriceBadge book={product} size="lg" />

          <div className="detail-meta">
            {(product.manufacturer || product.publisher) && (
              <div className="detail-meta__row">
                <span className="detail-meta__label">Fabricante</span>
                <strong className="detail-meta__value">{product.manufacturer || product.publisher}</strong>
              </div>
            )}

            {(product.publication_year || product.year) && (
              <div className="detail-meta__row">
                <span className="detail-meta__label">Año de lanzamiento</span>
                <strong className="detail-meta__value">{product.publication_year || product.year}</strong>
              </div>
            )}

            {model && (
              <div className="detail-meta__row">
                <span className="detail-meta__label">Modelo</span>
                <strong className="detail-meta__value">{model}</strong>
              </div>
            )}

            {condition && (
              <div className="detail-meta__row">
                <span className="detail-meta__label">Condición</span>
                <strong className="detail-meta__value">{condition}</strong>
              </div>
            )}

            <div className="detail-meta__row">
              <span className="detail-meta__label">Disponibilidad</span>
              <AvailabilityBadge stock={stock} />
            </div>

            {cartQuantity > 0 && (
              <div className="detail-meta__row">
                <span className="detail-meta__label">In Cart</span>
                <strong className="detail-meta__value">{cartQuantity} unidad(es)</strong>
              </div>
            )}
          </div>

          <p className="product-detail-description">
            {product.description || 'Especificaciones de hardware y recomendaciones técnicas para compatibilidad y rendimiento óptimos.'}
          </p>

          {isLocalFallback && (
            <p className="product-detail-warning">
              Este producto está disponible sólo como ejemplo de catálogo y no puede agregarse al pedido.
            </p>
          )}

          <button
            className="product-detail-buy-btn"
            disabled={!isAvailable || reachedStock || isLocalFallback}
            onClick={handleAdd}
          >
            {!isAvailable
              ? 'Agotado'
              : isLocalFallback
                ? 'No disponible para compra'
                : reachedStock
                  ? 'Cantidad máxima en el carrito'
                  : 'Agregar al carrito 🛒'}
          </button>
        </div>
      </section>

      <RecommendedBooks
        bookId={product.id}
        currentProduct={product}
        onBookClick={(bookId) => navigate('/producto/' + bookId)}
      />
    </main>
  )
}

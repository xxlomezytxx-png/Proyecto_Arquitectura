import { useEffect, useState } from 'react'
import { Sparkles, ArrowLeft, Loader2 } from 'lucide-react'
import { Link } from 'react-router-dom'
import { getBooks, getCategories } from '../api'
import { getRecommendations } from '../services/recommendationService'
import BookCard from '../components/BookCard'
import { HARDWARE_PRODUCTS, HARDWARE_CATEGORIES } from '../hardwareMock'

const SEED_COUNT = 6

export default function IAPicks() {
  const [picks, setPicks] = useState([])
  const [categories, setCategories] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    async function load() {
      try {
        const [productsData, cats] = await Promise.all([getBooks(), getCategories()])
        setCategories(cats || [])

        let allProducts = productsData.items || []
        const looksLikeBooks = allProducts.some(p => /\b(Cien años de soledad|Don Quijote|1984|Fahrenheit 451|Fahrenheit|Clean Code|DDD|El Quijote|Programación|libro|novela|ensayo|poesía|biografía|historia)\b/i.test(String(p.title || '')))
        if (looksLikeBooks || allProducts.length === 0) {
          allProducts = HARDWARE_PRODUCTS.map((item) => ({
            ...item,
            id: `fallback-${item.id}`,
            isFallback: true,
            is_fallback: true,
          }))
          setCategories(HARDWARE_CATEGORIES)
        } else {
          setCategories(cats || [])
        }

        const seeds = allProducts.slice(0, SEED_COUNT)
        const recommendedIds = new Set()
        const recProducts = []

        const recResults = await Promise.allSettled(
          seeds.map(p => getRecommendations(p.id))
        )

        for (const result of recResults) {
          if (result.status !== 'fulfilled') continue
          for (const rec of result.value || []) {
            const id = rec.book_id ?? rec.id
            if (id && !recommendedIds.has(id)) {
              recommendedIds.add(id)
              const full = allProducts.find(p => String(p.id) === String(id))
              if (full) recProducts.push(full)
            }
          }
        }

        if (recProducts.length === 0) {
          const shuffled = [...allProducts].sort(() => Math.random() - 0.5)
          setPicks(shuffled.slice(0, 12))
        } else {
          setPicks(recProducts.slice(0, 24))
        }
      } catch (err) {
        setError('Could not load gaming hardware recommendations.')
      } finally {
        setLoading(false)
      }
    }
    load()
  }, [])

  return (
    <div className="ia-picks-page">
      <div className="ia-picks-hero">
        <div className="ia-picks-hero-inner">
          <div className="ia-picks-badge">
            <Sparkles size={14} />
            Inteligencia Artificial
          </div>
          <h1 className="ia-picks-title">Centro IA Hardware</h1>
          <p className="ia-picks-subtitle">
            Computadores, componentes y mantenimiento seleccionados por IA según tendencias y compatibilidad.
          </p>
          <Link to="/" className="ia-picks-back">
            <ArrowLeft size={14} />
            Volver a la tienda
          </Link>
        </div>
      </div>

      <div className="ia-picks-content">
        {loading && (
          <div className="ia-picks-loading">
            <Loader2 size={28} className="spin" />
            <span>Analizando inventario de hardware con IA…</span>
          </div>
        )}

        {!loading && error && (
          <div className="ia-picks-error">{error}</div>
        )}

        {!loading && !error && (
          <>
            <p className="ia-picks-count">{picks.length} recomendaciones de hardware</p>
            <div className="product-grid">
              {picks.map(product => (
                <BookCard key={product.id} book={product} categories={categories} />
              ))}
            </div>
          </>
        )}
      </div>
    </div>
  )
}

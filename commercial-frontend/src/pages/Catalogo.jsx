import { useEffect, useMemo, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { AlertTriangle, PackageOpen, SlidersHorizontal, Sparkles } from 'lucide-react'
import { getBooks, getCategories } from '../api'
import BookCard from '../components/BookCard'
import { Checkbox } from '../components/ui'
import { HARDWARE_PRODUCTS, HARDWARE_CATEGORIES } from '../hardwareMock'



const COND_OPTIONS = ['Nuevo', 'Semi Nuevo', 'Usado', 'Reacondicionado']
const DISPLAY_PAGE_SIZE = 20

const SORT_OPTIONS = [
  { value: 'default', label: 'Relevancia' },
  { value: 'price_asc', label: 'Precio ↑' },
  { value: 'price_desc', label: 'Precio ↓' },
  { value: 'year_desc', label: 'Más recientes' },
]

const SKELETON_IDS = ['s0','s1','s2','s3','s4','s5','s6','s7','s8','s9','s10','s11']

function getCondition(product) {
  return product.condition ?? product.estado ?? product.estado_libro ?? product.book_condition ?? ''
}

const FEATURED_SECTIONS = [
  { label: 'Gaming PCs', keywords: ['PC', 'Gaming', 'PC Gamer', 'Desktop', 'Rig'] },
  { label: 'GPUs & Accelerators', keywords: ['GPU', 'Graphics', 'RTX', 'Radeon', 'Acceleration'] },
  { label: 'Monitors & Displays', keywords: ['Monitor', 'Screen', 'Display', 'Gaming', '144Hz', '4K'] },
  { label: 'SSDs & Storage', keywords: ['SSD', 'NVMe', 'Storage', 'Drive', 'M.2'] },
  { label: 'Maintenance & Repairs', keywords: ['Maintenance', 'Support', 'Repair', 'Technical', 'Thermal', 'Cleaning'] },
  { label: 'Gaming Peripherals', keywords: ['Keyboard', 'Mouse', 'Headset', 'Mousepad', 'Webcam', 'Controller'] },
]


function SortPill({ value, label, active, onClick }) {
  return (
    <button
      className={`sort-pill${active ? ' active' : ''}`}
      onClick={() => onClick(value)}
    >
      {label}
    </button>
  )
}

function productMatchesFilters(product, cleanQuery, cats, conds, maxPrice, brand, year) {
  const price = Number(product.price || product.suggested_price || 0)
  const condition = String(getCondition(product)).toLowerCase()

  if (cleanQuery) {
    const text = `${product.title || ''} ${product.brand || product.author || ''} ${product.isbn || ''} ${product.manufacturer || product.publisher || ''}`.toLowerCase()
    if (!text.includes(cleanQuery)) return false
  }

  const activeCats = Object.keys(cats).filter(id => cats[id])
  if (activeCats.length > 0 && !activeCats.some(id => Number(product.category_id) === Number(id))) return false

  const activeConds = Object.keys(conds).filter(k => conds[k])
  if (activeConds.length > 0 && !activeConds.some(c => condition.includes(c.toLowerCase()))) return false

  if (maxPrice && price > Number(maxPrice)) return false

  if (brand) {
    const br = (product.brand || product.author || '').toLowerCase()
    if (!br.includes(brand.toLowerCase())) return false
  }

  if (year) {
    const productYear = String(product.publication_year || product.year || '')
    if (!productYear.startsWith(year)) return false
  }

  return true
}

function sortProducts(products, sort) {
  if (sort === 'price_asc') return [...products].sort((a, b) => Number(a.price || a.suggested_price || 0) - Number(b.price || b.suggested_price || 0))
  if (sort === 'price_desc') return [...products].sort((a, b) => Number(b.price || b.suggested_price || 0) - Number(a.price || a.suggested_price || 0))
  if (sort === 'year_desc') return [...products].sort((a, b) => Number(b.publication_year || b.year || 0) - Number(a.publication_year || a.year || 0))
  return products
}

function getSectionTitle(cats, categories, searchQuery) {
  const activeCats = Object.keys(cats).filter(id => cats[id])
  if (activeCats.length === 1) return categories.find(c => String(c.id) === activeCats[0])?.name ?? 'Categoría'
  if (activeCats.length > 1) return 'Varias categorías'
  if (searchQuery) return `Resultados para "${searchQuery}"`
  return 'Tienda completa'
}

export default function Catalogo({ searchQuery = '' }) {
  const navigate = useNavigate()
  const [products, setProducts] = useState([])
  const [categories, setCategories] = useState([])
  const [cats, setCats] = useState({})
  const [conds, setConds] = useState({})
  const [maxPrice, setMaxPrice] = useState('')
  const [brand, setBrand] = useState('')
  const [year, setYear] = useState('')
  const [sort, setSort] = useState('default')
  const [page, setPage] = useState(1)
  const [loading, setLoading] = useState(true)
  const [serviceError, setServiceError] = useState(false)

  useEffect(() => {
    async function load() {
      setLoading(true)
      setServiceError(false)
      try {
        const [productsData, categoriesData] = await Promise.all([getBooks(), getCategories()])
        const activeProducts = productsData?.items || []
        const activeCategories = categoriesData || []

        const looksLikeBooks = activeProducts.some(p =>
          /\b(Cien años de soledad|Don Quijote|1984|Fahrenheit 451|Fahrenheit|Clean Code|DDD|El Quijote|Programación|libro|novela|ensayo|poesía|biografía|historia)\b/i.test(String(p.title || ''))
        )

        const looksLikeBookCategories = activeCategories.some(c =>
          /\b(libro|novela|ficción|ficcion|literatura|fantasía|fantasia|ensayo|poesía|poesia|cuento|autor|biografía|biografia|historia)\b/i.test(String(c.name || ''))
        )

        setProducts(looksLikeBooks || activeProducts.length === 0 ? HARDWARE_PRODUCTS.map((item) => ({
          ...item,
          id: `fallback-${item.id}`,
          isFallback: true,
          is_fallback: true,
        })) : activeProducts)
        setCategories(looksLikeBooks || looksLikeBookCategories || activeCategories.length === 0 ? HARDWARE_CATEGORIES : activeCategories)

        if ((productsData.items?.length || 0) === 0 && productsData._error) setServiceError(true)
      } catch {
        setProducts(HARDWARE_PRODUCTS)
        setCategories(HARDWARE_CATEGORIES)
        setServiceError(false)
      } finally {
        setLoading(false)
      }

    }
    load()
  }, [])

  const filteredProducts = useMemo(() => {
    const sanitizeQuery = (q) => {
      const v = (q ?? '').toString().trim()
      if (!v) return ''

      const lower = v.toLowerCase()
      // Si la IA manda un mensaje en vez de una consulta real, no filtre por ese texto.
      const looksLikeAiNotFound =
        /^no encontr[ée] productos/.test(lower) ||
        lower.includes('no encontré productos') ||
        lower.includes('no encontre productos') ||
        lower.includes('no encontré productos relacionados') ||
        lower.includes('no encontre productos relacionados') ||
        lower.includes('intenta buscar por nombre') ||
        lower.includes('intenta buscar por') ||
        lower.includes('no se encontraron productos') ||
        lower.includes('could not find') ||
        lower.includes('try searching');

      return looksLikeAiNotFound ? '' : lower
    }

    const cleanQuery = sanitizeQuery(searchQuery)
    const filtered = products.filter(product => productMatchesFilters(product, cleanQuery, cats, conds, maxPrice, brand, year))
    return sortProducts(filtered, sort)
  }, [products, searchQuery, cats, conds, maxPrice, brand, year, sort])

  const totalPages = Math.max(1, Math.ceil(filteredProducts.length / DISPLAY_PAGE_SIZE))
  const pagedProducts = filteredProducts.slice((page - 1) * DISPLAY_PAGE_SIZE, page * DISPLAY_PAGE_SIZE)

  const sectionTitle = getSectionTitle(cats, categories, searchQuery)

  const allPrices = products.map(p => Number(p.price || p.suggested_price || 0)).filter(p => p > 0)
  const priceMax = allPrices.length ? Math.ceil(Math.max(...allPrices)) : 200

  function toggleCat(id) {
    setPage(1)
    setCats(prev => ({ ...prev, [id]: !prev[id] }))
  }

  function activateFeature(keywords) {
    setPage(1)
    setCats(categories.reduce((acc, category) => {
      const active = keywords.some(keyword =>
        String(category.name || '').toLowerCase().includes(keyword.toLowerCase())
      )
      if (active) acc[category.id] = true
      return acc
    }, {}))
  }

  function toggleCond(label) {
    setPage(1)
    setConds(prev => ({ ...prev, [label]: !prev[label] }))
  }

  return (
    <>
      {!searchQuery && (
        <section className="hero">
          <h1 className="hero-title">Tu próxima actualización de hardware: PCs, GPUs, monitores y más</h1>
          <p className="hero-sub">Encuentra PCs, GPUs, monitores, almacenamiento SSD y servicios de soporte técnico con envío rápido y sin complicaciones.</p>
          <div className="hero-highlights">
            <span>PCs Gamer</span>
            <span>GPUs</span>
            <span>Monitores</span>
            <span>SSDs</span>
            <span>Mantenimiento</span>
            <span>Periféricos</span>
          </div>

          <div className="featured-sections">
            {FEATURED_SECTIONS.map(section => (
              <button
                key={section.label}
                className="featured-section-card"
                onClick={() => activateFeature(section.keywords)}
                type="button"
              >
                <span>{section.label}</span>
                <small>Ver</small>
              </button>
            ))}
          </div>
        </section>
      )}

      <div className="catalog-wrap">
        <aside className="sidebar">
          <div className="sidebar-section">
            <div className="sidebar-title">
              <SlidersHorizontal size={14} />
              Categorías
            </div>
            <ul className="sidebar-filter-list">
              {categories.map(cat => (
                <li key={cat.id} className="sidebar-filter-item">
                  <label className="sidebar-filter-label">
                    <Checkbox
                      checked={!!cats[cat.id]}
                      onChange={() => toggleCat(String(cat.id))}
                    />
                    {cat.name}
                  </label>
                </li>
              ))}
            </ul>
          </div>

          <div className="sidebar-section">
            <div className="sidebar-title">Condición</div>
            <ul className="sidebar-filter-list">
              {COND_OPTIONS.map(label => (
                <li key={label} className="sidebar-filter-item">
                  <label className="sidebar-filter-label">
                    <Checkbox
                      checked={!!conds[label]}
                      onChange={() => toggleCond(label)}
                    />
                    {label}
                  </label>
                </li>
              ))}
            </ul>
          </div>

          <div className="sidebar-section">
            <div className="sidebar-title">Marca o fabricante</div>
            <input
              className="sidebar-text-input"
              type="text"
              placeholder="Filter by brand…"
              value={brand}
              onChange={e => { setBrand(e.target.value); setPage(1) }}
            />
          </div>

          <div className="sidebar-section">
            <div className="sidebar-title">Año de lanzamiento</div>
            <input
              className="sidebar-text-input"
              type="number"
              placeholder="E.g: 2024"
              value={year}
              onChange={e => { setYear(e.target.value); setPage(1) }}
            />
          </div>

          <div className="sidebar-section">
            <div className="sidebar-title">Max Price</div>
            <div className="sidebar-price-row">
              <span className="sidebar-price-label">up to</span>
              <span className="sidebar-price-value">
                {maxPrice ? `$${Number(maxPrice).toFixed(0)}` : 'any'}
              </span>
            </div>
            <input
              type="range"
              min={0}
              max={priceMax}
              step={1}
              value={maxPrice || priceMax}
              onChange={e => setMaxPrice(e.target.value === String(priceMax) ? '' : e.target.value)}

              className="sidebar-price-range"
            />
          </div>

          <div className="sidebar-ai-card">
            <div className="sidebar-ai-title">
              <Sparkles size={14} />
              AI Recommendations
            </div>
            <p className="sidebar-ai-desc">Discover gaming hardware & peripherals selected for you based on your preferences.</p>
            <button className="sidebar-ai-btn" onClick={() => navigate('/ia-picks')}>Ver IA</button>
          </div>
        </aside>

        <main className="store-main">
          <div className="section-header">
            <h2 className="section-title">{sectionTitle}</h2>
            <span className="section-count">{filteredProducts.length} items</span>
          </div>



          <div className="sort-pills">
            {SORT_OPTIONS.map(opt => (
              <SortPill
                key={opt.value}
                value={opt.value}
                label={opt.label}
                active={sort === opt.value}
                onClick={setSort}
              />
            ))}
          </div>

          {loading && (
            <div className="product-grid">
              {SKELETON_IDS.map(id => (
                <div key={id} className="product-skeleton" />
              ))}
            </div>
          )}

          {!loading && serviceError && (
      <div className="empty-state">
              <div className="empty-icon"><AlertTriangle size={40} /></div>
              <p className="empty-text">La tienda no está disponible</p>
              <p className="empty-sub">Could not load gaming inventory. Please reload the page.</p>

            </div>

          )}

          {!loading && !serviceError && filteredProducts.length === 0 && (
            <div className="empty-state">
              <div className="empty-icon"><PackageOpen size={40} /></div>
              <p className="empty-text">No gaming items found</p>
              <p className="empty-sub">Prueba con diferentes filtros o términos de búsqueda</p>

            </div>
          )}

          {!loading && !serviceError && filteredProducts.length > 0 && (
            <>
              <div className="product-grid">
                {pagedProducts.map(product => (
                  <BookCard key={product.id} book={product} categories={categories} />
                ))}
              </div>

              {totalPages > 1 && (
                <div className="pagination">
                  <button
                    className="page-btn"
                    disabled={page === 1}
                    onClick={() => setPage(p => p - 1)}
                  >
                    ← Previous
                  </button>
                  <span className="page-info">Page {page} of {totalPages}</span>
                  <button
                    className="page-btn"
                    disabled={page === totalPages}
                    onClick={() => setPage(p => p + 1)}
                  >
                    Next →
                  </button>
                </div>
              )}
            </>
          )}
        </main>
      </div>
    </>
  )
}

import PropTypes from 'prop-types'

const EMPTY_FILTERS = {
  condition: '',
  publisher: '',
  publication_year: '',
  min_price: '',
  max_price: '',
}

export default function CatalogFilters({ filters, setFilters }) {
  const update = (field, value) =>
    setFilters(prev => ({ ...prev, [field]: value }))

  const clearFilters = () => setFilters(EMPTY_FILTERS)

  const hasActive = Object.values(filters).some(v => v !== '')

  return (
    <div className="filters-wrap">
      <div className="filters-inner">
        <div className="catalog-filters">
          <div className="filter-row">
            <div className="filter-group">
              <span className="filter-label">Condición</span>
              <select
                className="filter-select"
                value={filters.condition}
                onChange={e => update('condition', e.target.value)}
              >
                <option value="">Todas</option>
                <option value="nuevo">Nuevo</option>
                <option value="bueno">Bueno</option>
                <option value="aceptable">Aceptable</option>
                <option value="deteriorado">Reacondicionado</option>
              </select>
            </div>

            <div className="filter-group">
              <span className="filter-label">Marca</span>
              <input
                className="filter-input"
                value={filters.publisher}
                onChange={e => update('publisher', e.target.value)}
                placeholder="Marca"
              />
            </div>

            <div className="filter-group">
              <span className="filter-label">Año</span>
              <input
                className="filter-input"
                type="number"
                value={filters.publication_year}
                onChange={e => update('publication_year', e.target.value)}
                placeholder="Año"
                style={{ minWidth: 80 }}
              />
            </div>

            <div className="filter-group">
              <span className="filter-label">Precio mínimo</span>
              <input
                className="filter-input"
                type="number"
                value={filters.min_price}
                onChange={e => update('min_price', e.target.value)}
                placeholder="$ Min"
              />
            </div>

            <div className="filter-group">
              <span className="filter-label">Precio máximo</span>
              <input
                className="filter-input"
                type="number"
                value={filters.max_price}
                onChange={e => update('max_price', e.target.value)}
                placeholder="$ Max"
              />
            </div>

            {hasActive && (
              <button className="filter-clear-btn" onClick={clearFilters}>
                Limpiar filtros
              </button>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}

CatalogFilters.propTypes = {
  filters: PropTypes.shape({
    condition: PropTypes.string,
    publisher: PropTypes.string,
    publication_year: PropTypes.string,
    min_price: PropTypes.string,
    max_price: PropTypes.string,
  }).isRequired,
  setFilters: PropTypes.func.isRequired,
}

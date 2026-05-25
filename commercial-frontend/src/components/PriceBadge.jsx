export default function PriceBadge({ book, size = 'md' }) {
  const price = book?.suggested_price || book?.price

  if (!price) {
    return (
      <p className={`price-badge ${size}`}>
        Price upon request
      </p>
    )
  }

  return (
    <div className="price-badge-row">
      <p className={`price-badge ${size}`}>
        ${Number(price).toLocaleString('es-CO')}
      </p>
      <span className={`price-source-badge ${book?.is_fallback ? 'badge-estimado' : 'badge-verificado'}`}>
        {book?.is_fallback ? 'Estimated' : 'Verified'}
      </span>
    </div>
  )
}

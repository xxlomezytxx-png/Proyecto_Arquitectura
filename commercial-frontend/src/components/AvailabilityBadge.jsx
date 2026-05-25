export default function AvailabilityBadge({ stock }) {
  const value = stock === undefined || stock === null || stock === '' ? null : Number(stock)

  if (value === null || Number.isNaN(value)) {
    return <span className="badge-stock available">En stock</span>
  }

  if (value <= 0) {
    return <span className="badge-stock soldout">Agotado</span>
  }

  return (
    <span className="badge-stock available">
      En stock: {value} unidad(es)
    </span>
  )
}
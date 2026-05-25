import { useState } from 'react'
import { getPlaceholderUrl } from '../api'

export default function EnrichedBookImage({ book, height = 220, borderRadius = '12px' }) {
  const [hasError, setHasError] = useState(false)

  const image =
    !hasError && book?.cover_url
      ? book.cover_url
      : getPlaceholderUrl(book?.title || 'Hardware')

  return (
    <img
      src={image}
      alt={book?.title || 'Imagen del producto'}
      onError={() => setHasError(true)}
      style={{
        width: '100%',
        height,
        objectFit: 'cover',
        borderRadius,
        background: '#2F6F52'
      }}
    />
  )
}
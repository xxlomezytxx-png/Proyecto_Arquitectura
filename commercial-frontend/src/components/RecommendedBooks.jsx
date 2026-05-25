import { useState, useEffect } from "react";
import { getRecommendations } from "../services/recommendationService";
import { HARDWARE_PRODUCTS } from "../hardwareMock";

const BOOK_MATCHER = /\b(libro|novela|ficción|ficcion|literatura|fantasía|fantasia|ensayo|poesía|poesia|cuento|autor|biografía|biografia|historia|1984|don quijote|cien años|farenheit|martin|jostein|borges)\b/i;

function isLegacyBookItem(product) {
  const title = String(product.title || '').toLowerCase();
  const category = String(product.category || '').toLowerCase();
  return BOOK_MATCHER.test(title) || BOOK_MATCHER.test(category);
}

function getHardwareFallback(currentProduct) {
  const keywords = [currentProduct?.category, currentProduct?.brand, currentProduct?.title]
    .filter(Boolean)
    .join(' ')
    .toLowerCase();

  const fallback = HARDWARE_PRODUCTS.filter((item) => {
    const itemText = `${item.title} ${item.category} ${item.brand}`.toLowerCase();
    return keywords.split(/\s+/).some((keyword) => keyword.length > 3 && itemText.includes(keyword));
  });

  return fallback.length ? fallback.slice(0, 6) : HARDWARE_PRODUCTS.slice(0, 6);
}

export default function RecommendedBooks({ bookId, currentProduct, onBookClick }) {
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!bookId) return;
    let mounted = true;
    setLoading(true);

    getRecommendations(bookId)
      .then((raw) => {
        if (!mounted) return;
        const mapped = (raw || []).map((item) => {
          const recommendedId = item.book_id ?? item.id;
          const localHardware = HARDWARE_PRODUCTS.find((hw) => String(hw.id) === String(recommendedId));
          if (localHardware) {
            return {
              ...localHardware,
              id: `fallback-${localHardware.id}`,
              isFallback: true,
              is_fallback: true,
              reason: item.reason || item.reason_text || 'Recomendado para tu equipo',
              source_id: recommendedId,
            };
          }
          return {
            ...item,
            reason: item.reason || 'Recomendado para tu equipo',
          };
        });

        const hasHardware = mapped.some((item) => !isLegacyBookItem(item));
        const finalProducts = hasHardware ? mapped.slice(0, 6) : getHardwareFallback(currentProduct);
        setProducts(finalProducts);
      })
      .catch(() => {
        if (!mounted) return;
        setProducts(getHardwareFallback(currentProduct));
      })
      .finally(() => {
        if (!mounted) return;
        setLoading(false);
      });

    return () => {
      mounted = false;
    };
  }, [bookId, currentProduct]);

  if (loading) return <div className="recommended-loading">Cargando componentes compatibles...</div>;
  if (!products.length) return null;

  return (
    <section className="recommended-section">
      <h3 className="recommended-title">Componentes recomendados</h3>
      <div className="recommended-scroll">
        {products.map((product) => {
          const targetId = product.id ?? product.book_id ?? product.source_id;
          return (
            <button
              key={targetId}
              className="recommended-card"
              onClick={() => onBookClick?.(targetId)}
            >
              <div className="recommended-card__placeholder">
                {(product.title || "?")[0].toUpperCase()}
              </div>
              <p className="recommended-card__title">{product.title}</p>
              <p className="recommended-card__author">{product.brand || product.manufacturer || 'Marca'} · {product.category || 'Categoría'}</p>
              <span className="recommended-card__reason">{product.reason || 'Compatible con tu configuración'}</span>
            </button>
          );
        })}
      </div>
    </section>
  );
}

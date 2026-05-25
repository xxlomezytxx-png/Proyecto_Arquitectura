import { useEffect, useState, Fragment } from "react";
import PricingFilters, { FilterState } from "./PricingFilters";
import PricingExplanation from "./PricingExplanation";
import PricingHistory from "./PricingHistory";
import { getPricingList, bulkCalculate, recalculatePrice, getCatalogProducts } from "../../services/pricingService";
import styles from "./PricingDashboard.module.css";

interface PricingItem {
  book_id: string;
  title: string;
  condition: string;
  price: number;
  isFallback: boolean;
  enrichedFlag: boolean;
}

const INITIAL_FILTERS: FilterState = {
  source: "all",
  condition: "",
  minPrice: "",
  maxPrice: "",
};

const formatCOP = (value: number) =>
  new Intl.NumberFormat("es-CO", {
    style: "currency",
    currency: "COP",
    maximumFractionDigits: 0,
  }).format(Number(value || 0));

const parseError = (err: unknown, fallback: string): string => {
  if (err && typeof err === "object") {
    const e = err as { response?: { status?: number; data?: { detail?: string } }; message?: string };
    if (e.response?.status) return `Error ${e.response.status}: ${e.response.data?.detail ?? fallback}`;
    if (e.message) return `Sin respuesta del servidor: ${e.message}`;
  }
  return fallback;
};

const PricingDashboard = () => {
  const [data, setData] = useState<PricingItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [calculating, setCalculating] = useState(false);
  const [error, setError] = useState("");
  const [filters, setFilters] = useState<FilterState>(INITIAL_FILTERS);
  const [expandedId, setExpandedId] = useState<string | null>(null);
  const [prices, setPrices] = useState<Record<string, number>>({});
  const [historyKeys, setHistoryKeys] = useState<Record<string, number>>({});
  const [recalcLoading, setRecalcLoading] = useState<Record<string, boolean>>({});
  const [recalcError, setRecalcError] = useState<Record<string, string>>({});

  const load = async () => {
    setLoading(true);
    setError("");
    try {
      const [pricingResult, catalogResult] = await Promise.allSettled([
        getPricingList(),
        getCatalogProducts(),
      ]);

      if (pricingResult.status === "rejected") throw pricingResult.reason;
      const res = pricingResult.value;

      const enrichmentMap: Record<string, boolean> = {};
      if (catalogResult.status === "fulfilled") {
        const raw = catalogResult.value;
        const books: Record<string, unknown>[] = Array.isArray(raw) ? raw : (raw?.books ?? raw?.items ?? []);
        for (const b of books) {
          enrichmentMap[String(b.id ?? "")] = Boolean(b.enriched_flag);
        }
      }

      const items: PricingItem[] = (res.items || res || []).map((item: Record<string, unknown>) => {
        const id = String(item.book_id ?? item.id ?? "");
        return {
          book_id: id,
          title: String(item.title ?? item.book_id ?? "Sin título"),
          condition: String(item.condition ?? "BUENO"),
          price: Number(item.suggested_price ?? item.price ?? 0),
          isFallback: Boolean(item.is_fallback ?? item.isFallback ?? false),
          enrichedFlag: enrichmentMap[id] ?? false,
        };
      });
      setData(items);
    } catch (err: unknown) {
      setError(parseError(err, "No se pudo conectar con el servicio de pricing."));
      setData([]);
    } finally {
      setLoading(false);
    }
  };

  const handleBulkCalculate = async () => {
    setCalculating(true);
    setError("");
    try {
      await bulkCalculate();
      await load();
    } catch (err: unknown) {
      setError(parseError(err, "Error al calcular precios del catálogo."));
    } finally {
      setCalculating(false);
    }
  };

  const handleRecalculate = async (bookId: string, title: string, condition: string) => {
    setRecalcLoading((prev) => ({ ...prev, [bookId]: true }));
    setRecalcError((prev) => ({ ...prev, [bookId]: "" }));
    try {
      const res = await recalculatePrice(bookId, title, condition);
      const newPrice = res.suggested_price ?? res.price;
      setPrices((prev) => ({ ...prev, [bookId]: newPrice }));
      setHistoryKeys((prev) => ({ ...prev, [bookId]: (prev[bookId] ?? 0) + 1 }));
    } catch {
      setRecalcError((prev) => ({
        ...prev,
        [bookId]: "No se pudo recalcular el precio. Intente de nuevo.",
      }));
    } finally {
      setRecalcLoading((prev) => ({ ...prev, [bookId]: false }));
    }
  };

  useEffect(() => { load(); }, []);

  const filtered = data.filter((item) => {
    const currentPrice = prices[item.book_id] ?? item.price;
    if (filters.source === "verified" && item.isFallback) return false;
    if (filters.source === "estimated" && !item.isFallback) return false;
    if (filters.condition && item.condition !== filters.condition) return false;
    if (filters.minPrice && currentPrice < Number(filters.minPrice)) return false;
    if (filters.maxPrice && currentPrice > Number(filters.maxPrice)) return false;
    return true;
  });

  const verifiedCount = data.filter((i) => !i.isFallback).length;
  const estimatedCount = data.filter((i) => i.isFallback).length;
  const enrichedCount = data.filter((i) => i.enrichedFlag).length;
  const avgPrice = data.length
    ? (data.reduce((s, i) => s + (prices[i.book_id] ?? i.price), 0) / data.length).toFixed(2)
    : "0.00";

  return (
    <div className={styles.page}>
      <div className={styles.pageHeader}>
        <div>
          <h1 className={styles.pageTitle}>Panel de Precios</h1>
          <p className={styles.pageSubtitle}>Motor de pricing inteligente con trazabilidad completa</p>
        </div>
        <div style={{ display: "flex", gap: "0.5rem" }}>
          <button
            className={styles.refreshBtn}
            onClick={handleBulkCalculate}
            disabled={calculating || loading}
          >
            {calculating ? "Calculando…" : "⚡ Calcular catálogo"}
          </button>
          <button className={styles.refreshBtn} onClick={load} disabled={loading || calculating}>
            {loading ? "Cargando…" : "↻ Actualizar"}
          </button>
        </div>
      </div>

      <div className={styles.kpiRow}>
        <div className={`${styles.kpi} ${styles.kpiBlue}`}>
          <span className={styles.kpiNum}>{data.length}</span>
          <span className={styles.kpiLabel}>Total productos</span>
        </div>
        <div className={`${styles.kpi} ${styles.kpiGreen}`}>
          <span className={styles.kpiNum}>{verifiedCount}</span>
          <span className={styles.kpiLabel}>Verificados</span>
        </div>
        <div className={`${styles.kpi} ${styles.kpiOrange}`}>
          <span className={styles.kpiNum}>{estimatedCount}</span>
          <span className={styles.kpiLabel}>Estimados</span>
        </div>
        <div className={`${styles.kpi} ${styles.kpiPurple}`}>
          <span className={styles.kpiNum}>{formatCOP(Number(avgPrice))}</span>
          <span className={styles.kpiLabel}>Precio promedio</span>
        </div>
        <div className={`${styles.kpi} ${styles.kpiTeal}`}>
          <span className={styles.kpiNum}>{enrichedCount}</span>
          <span className={styles.kpiLabel}>Enriquecidos IA</span>
        </div>
      </div>

      <PricingFilters filters={filters} setFilters={setFilters} />

      {loading && (
        <div className={styles.stateWrap}>
          <div className={styles.spinner} />
          <p className={styles.stateText}>Obteniendo precios…</p>
        </div>
      )}

      {!loading && error && (
        <div className={styles.errorBox}>
          <span>⚠️</span> {error}
        </div>
      )}

      {!loading && !error && filtered.length === 0 && (
        <div className={styles.stateWrap}>
          <p className={styles.stateText}>
            {data.length === 0
              ? "Aún no hay precios calculados. Usa ⚡ Calcular catálogo para iniciar."
              : "No hay libros con los filtros seleccionados."}
          </p>
          {data.length === 0 && (
            <button
              className={styles.refreshBtn}
              onClick={handleBulkCalculate}
              disabled={calculating}
              style={{ marginTop: "1rem" }}
            >
              {calculating ? "Calculando…" : "⚡ Calcular catálogo"}
            </button>
          )}
        </div>
      )}

      {!loading && !error && filtered.length > 0 && (
        <div className={styles.tableWrap}>
          <table className={styles.table}>
            <thead>
              <tr>
                <th className={styles.th}>Título</th>
                <th className={styles.th}>Condición</th>
                <th className={styles.th}>Precio</th>
                <th className={styles.th}>Fuente</th>
                <th className={styles.th}>Estado IA</th>
                <th className={styles.th}>Acciones</th>
              </tr>
            </thead>
            <tbody>
              {filtered.map((item) => {
                const currentPrice = prices[item.book_id] ?? item.price;
                const isExpanded = expandedId === item.book_id;
                const isRecalculating = recalcLoading[item.book_id] ?? false;
                const rowError = recalcError[item.book_id] ?? "";
                const hKey = historyKeys[item.book_id] ?? 0;

                return (
                  <Fragment key={item.book_id}>
                    <tr className={styles.tr}>
                      <td className={`${styles.td} ${styles.titleCell}`} title={item.title}>{item.title}</td>
                      <td className={styles.td}>{item.condition}</td>
                      <td className={`${styles.td} ${styles.priceCell}`}>
                        {formatCOP(Number(currentPrice))}
                      </td>
                      <td className={styles.td}>
                        <span className={item.isFallback ? styles.badgeEstimated : styles.badgeVerified}>
                          {item.isFallback ? "Estimado" : "Verificado"}
                        </span>
                      </td>
                      <td className={styles.td}>
                        <span className={item.enrichedFlag ? styles.badgeEnriched : styles.badgePending}>
                          {item.enrichedFlag ? "Enriquecido" : "Pendiente"}
                        </span>
                      </td>
                      <td className={`${styles.td} ${styles.actions}`}>
                        <button
                          className={styles.btnSecondary}
                          onClick={() => setExpandedId(isExpanded ? null : item.book_id)}
                        >
                          {isExpanded ? "Ocultar" : "Detalle"}
                        </button>
                        <button
                          className={styles.btnPrimary}
                          onClick={() => handleRecalculate(item.book_id, item.title, item.condition)}
                          disabled={isRecalculating}
                        >
                          {isRecalculating ? "Calculando…" : "Recalcular"}
                        </button>
                      </td>
                    </tr>

                    {rowError && (
                      <tr className={styles.rowError}>
                        <td colSpan={6} className={styles.td}>⚠️ {rowError}</td>
                      </tr>
                    )}

                    {isExpanded && (
                      <tr className={styles.expandRow}>
                        <td colSpan={6} className={styles.expandCell}>
                          <PricingExplanation bookId={item.book_id} />
                          <PricingHistory key={hKey} bookId={item.book_id} />
                        </td>
                      </tr>
                    )}
                  </Fragment>
                );
              })}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
};

export default PricingDashboard;

import { useState, useEffect } from "react";
import { getPriceHistory } from "../../services/pricingService";
import styles from "./PricingHistory.module.css";

interface HistoryEntry {
  suggested_price: number;
  created_at: string;
  source: string;
  is_fallback: boolean;
}

interface Props {
  bookId: string;
}

const PricingHistory = ({ bookId }: Props) => {
  const [history, setHistory] = useState<HistoryEntry[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    const load = async () => {
      setLoading(true);
      setError("");
      try {
        const res = await getPriceHistory(bookId);
        setHistory(Array.isArray(res) ? res : (res.items ?? []));
      } catch {
        setError("No se pudo cargar el historial.");
      } finally {
        setLoading(false);
      }
    };
    load();
  }, [bookId]);

  if (loading) return <p className={styles.loading}>Cargando historial…</p>;
  if (error) return <p className={styles.error}>{error}</p>;
  if (history.length === 0) return <p className={styles.empty}>Sin historial disponible.</p>;

  return (
    <div className={styles.wrap}>
      <h4 className={styles.heading}>Historial de precios</h4>
      <ul className={styles.list}>
        {history.map((entry, i) => (
          <li key={i} className={styles.entry}>
            <span className={styles.price}>${Number(entry.suggested_price).toFixed(2)}</span>
            <span className={styles.date}>
              {new Date(entry.created_at).toLocaleString("es-CO", {
                dateStyle: "medium",
                timeStyle: "short",
              })}
            </span>
            <span className={entry.is_fallback ? styles.fallback : styles.verified}>
              {entry.is_fallback ? "Estimado" : "Verificado"}
            </span>
          </li>
        ))}
      </ul>
    </div>
  );
};

export default PricingHistory;

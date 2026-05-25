import { useState, useEffect } from "react";
import { getBookDetail } from "../../services/pricingService";
import styles from "./PricingExplanation.module.css";

interface BookDetail {
  suggested_price: number;
  base_price: number;
  condition_factor: number;
  source: string;
  references_used: number;
  explanation: string;
  is_fallback: boolean;
}

interface Props {
  bookId: string;
}

const PricingExplanation = ({ bookId }: Props) => {
  const [detail, setDetail] = useState<BookDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    const fetchDetail = async () => {
      setLoading(true);
      setError("");
      try {
        const res = await getBookDetail(bookId);
        setDetail(res);
      } catch {
        setError("No se pudo cargar el desglose del precio.");
      } finally {
        setLoading(false);
      }
    };
    fetchDetail();
  }, [bookId]);

  if (loading) return <p className={styles.loading}>Cargando desglose…</p>;
  if (error) return <p className={styles.error}>{error}</p>;
  if (!detail) return null;

  return (
    <div className={styles.wrap}>
      <h4 className={styles.heading}>Desglose del cálculo</h4>
      <div className={styles.grid}>
        <div className={styles.row}>
          <span className={styles.label}>Precio base</span>
          <span className={styles.value}>${Number(detail.base_price).toFixed(2)}</span>
        </div>
        <div className={styles.row}>
          <span className={styles.label}>Factor condición</span>
          <span className={styles.value}>{detail.condition_factor}</span>
        </div>
        <div className={styles.row}>
          <span className={styles.label}>Fuente</span>
          <span className={styles.value}>{detail.source ?? "—"}</span>
        </div>
        <div className={styles.row}>
          <span className={styles.label}>Referencias</span>
          <span className={styles.value}>{detail.references_used ?? 0}</span>
        </div>
        <div className={styles.row}>
          <span className={styles.label}>Precio sugerido</span>
          <span className={`${styles.value} ${styles.highlight}`}>
            ${Number(detail.suggested_price).toFixed(2)}
          </span>
        </div>
      </div>
      {detail.explanation && (
        <p className={styles.explanation}>{detail.explanation}</p>
      )}
    </div>
  );
};

export default PricingExplanation;

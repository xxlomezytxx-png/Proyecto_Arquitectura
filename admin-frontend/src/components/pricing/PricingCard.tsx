import { useState } from "react";
import PricingExplanation from "./PricingExplanation";
import PricingHistory from "./PricingHistory";
import { recalculatePrice } from "../../services/pricingService";
import styles from "./PricingCard.module.css";

interface PricingItem {
  book_id: string;
  title: string;
  condition: string;
  price: number;
  isFallback: boolean;
}

interface Props {
  data: PricingItem;
  onRecalculated?: (bookId: string, newPrice: number) => void;
}

const PricingCard = ({ data, onRecalculated }: Props) => {
  const [price, setPrice] = useState(data.price);
  const [show, setShow] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [historyKey, setHistoryKey] = useState(0);

  const handleRecalculate = async () => {
    setLoading(true);
    setError("");
    try {
      const res = await recalculatePrice(data.book_id, data.title, data.condition ?? "BUENO");
      const newPrice = res.suggested_price ?? res.price;
      setPrice(newPrice);
      setHistoryKey((k) => k + 1);
      onRecalculated?.(data.book_id, newPrice);
    } catch {
      setError("No se pudo recalcular el precio. Intente de nuevo.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className={styles.card}>
      <div className={styles.header}>
        <h3 className={styles.title}>{data.title}</h3>
        <span className={data.isFallback ? styles.estimated : styles.verified}>
          {data.isFallback ? "Estimado" : "Verificado"}
        </span>
      </div>

      <p className={styles.price}>${Number(price).toFixed(2)}</p>
      <p className={styles.condition}>Condición: {data.condition}</p>

      {error && <p className={styles.errorMsg}>{error}</p>}

      <div className={styles.buttons}>
        <button className={styles.buttonSecondary} onClick={() => setShow(!show)}>
          {show ? "Ocultar" : "Detalle"}
        </button>
        <button className={styles.buttonPrimary} onClick={handleRecalculate} disabled={loading}>
          {loading ? "Calculando…" : "Recalcular"}
        </button>
      </div>

      {show && (
        <div className={styles.detail}>
          <PricingExplanation bookId={data.book_id} />
          <PricingHistory key={historyKey} bookId={data.book_id} />
        </div>
      )}
    </div>
  );
};

export default PricingCard;

import styles from "./PricingFilters.module.css";

export interface FilterState {
  source: string;
  condition: string;
  minPrice: string;
  maxPrice: string;
}

interface Props {
  filters: FilterState;
  setFilters: (value: FilterState) => void;
}

const SOURCE_OPTIONS = [
  { value: "all",       label: "Todos",       icon: "📋" },
  { value: "verified",  label: "Verificados",  icon: "✅" },
  { value: "estimated", label: "Estimados",    icon: "⚠️" },
];

const CONDITION_OPTIONS = [
  { value: "",            label: "Todas" },
  { value: "NUEVO",       label: "Nuevo" },
  { value: "BUENO",       label: "Bueno" },
  { value: "ACEPTABLE",   label: "Aceptable" },
  { value: "DETERIORADO", label: "Deteriorado" },
];

const PricingFilters = ({ filters, setFilters }: Props) => {
  const set = (patch: Partial<FilterState>) =>
    setFilters({ ...filters, ...patch });

  return (
    <div className={styles.wrap}>
      <div className={styles.group}>
        <span className={styles.groupLabel}>Fuente</span>
        <div className={styles.bar}>
          {SOURCE_OPTIONS.map((f) => (
            <button
              key={f.value}
              className={`${styles.chip} ${filters.source === f.value ? styles.active : ""}`}
              onClick={() => set({ source: f.value })}
            >
              <span>{f.icon}</span> {f.label}
            </button>
          ))}
        </div>
      </div>

      <div className={styles.group}>
        <span className={styles.groupLabel}>Condición</span>
        <div className={styles.bar}>
          {CONDITION_OPTIONS.map((c) => (
            <button
              key={c.value}
              className={`${styles.chip} ${filters.condition === c.value ? styles.active : ""}`}
              onClick={() => set({ condition: c.value })}
            >
              {c.label}
            </button>
          ))}
        </div>
      </div>

      <div className={styles.group}>
        <span className={styles.groupLabel}>Rango de precio</span>
        <div className={styles.priceRange}>
          <input
            type="number"
            className={styles.priceInput}
            placeholder="Mín"
            value={filters.minPrice}
            onChange={(e) => set({ minPrice: e.target.value })}
            min={0}
          />
          <span className={styles.priceSep}>–</span>
          <input
            type="number"
            className={styles.priceInput}
            placeholder="Máx"
            value={filters.maxPrice}
            onChange={(e) => set({ maxPrice: e.target.value })}
            min={0}
          />
        </div>
      </div>
    </div>
  );
};

export default PricingFilters;

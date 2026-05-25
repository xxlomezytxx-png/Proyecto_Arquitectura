import React from "react";

const FILTROS = [
  { label: "Todos",      value: "" },
  { label: "Completado", value: "COMPLETADO" },
  { label: "Error",      value: "ERROR" },
  { label: "Procesado",  value: "PROCESADO" },
];

const Filtros = ({ setFiltroEstado, filtroActual = "" }) => {
  return (
    <div style={wrap}>
      {FILTROS.map(({ label, value }) => (
        <button
          key={value}
          style={btn(filtroActual === value)}
          onClick={() => setFiltroEstado(value)}
        >
          {label}
        </button>
      ))}
    </div>
  );
};

export default Filtros;


const wrap = { display: "flex", gap: "8px", marginBottom: "20px", flexWrap: "wrap" };

const btn = (active) => ({
  padding: "7px 14px",
  borderRadius: "6px",
  border: `1px solid ${active ? "#3b82f6" : "#1e293b"}`,
  background: active ? "#1e3a5f" : "#020617",
  color: active ? "#60a5fa" : "#94a3b8",
  fontSize: "13px",
  fontWeight: active ? "500" : "400",
  cursor: "pointer",
  transition: "all 0.15s ease",
});

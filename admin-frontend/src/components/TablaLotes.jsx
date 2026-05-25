import React from "react";

const TablaLotes = ({ lotes, onSelect }) => {
  if (lotes.length === 0) {
    return (
      <div style={emptyWrap}>
        <p style={emptyText}>No hay lotes que coincidan con el filtro aplicado.</p>
      </div>
    );
  }

  return (
    <div style={container}>
      <div style={header}>
        <span>ID</span>
        <span>Archivo</span>
        <span>Estado</span>
        <span style={{ textAlign: "right" }}>Válidos</span>
        <span style={{ textAlign: "right" }}>Inválidos</span>
        <span></span>
      </div>

      {lotes.map((l) => (
        <div key={l.id} style={row}>
          <span style={idStyle}>{l.id}</span>
          <span style={fileStyle}>{l.file_name || "—"}</span>
          <span style={getEstadoStyle(l.status)}>{l.status}</span>
          <span style={numStyle}>{l.valid_rows}</span>
          <span style={numStyle}>{l.invalid_rows}</span>
          <button style={button} onClick={() => onSelect(l)}>
            Ver
          </button>
        </div>
      ))}
    </div>
  );
};

export default TablaLotes;


/* ================= ESTILOS ================= */

const container = {
  marginTop: "20px",
  border: "1px solid #1e293b",
  borderRadius: "12px",
  overflow: "hidden",
  background: "#020617",
};

const header = {
  display: "grid",
  gridTemplateColumns: "60px 1fr 130px 80px 80px 80px",
  padding: "12px 20px",
  fontSize: "11px",
  color: "#64748b",
  letterSpacing: "0.5px",
  borderBottom: "1px solid #1e293b",
};

const row = {
  display: "grid",
  gridTemplateColumns: "60px 1fr 130px 80px 80px 80px",
  padding: "14px 20px",
  alignItems: "center",
  fontSize: "13px",
  borderBottom: "1px solid #1e293b",
  transition: "background 0.15s ease",
};

const idStyle = { fontWeight: "600", color: "#e2e8f0" };

const fileStyle = {
  color: "#94a3b8",
  overflow: "hidden",
  textOverflow: "ellipsis",
  whiteSpace: "nowrap",
};

const numStyle = { textAlign: "right", fontVariantNumeric: "tabular-nums" };

const button = {
  background: "transparent",
  border: "1px solid #1e293b",
  padding: "5px 10px",
  borderRadius: "6px",
  fontSize: "12px",
  cursor: "pointer",
  color: "#e2e8f0",
};

const emptyWrap = {
  marginTop: "20px",
  background: "#020617",
  border: "1px solid #1e293b",
  borderRadius: "12px",
  padding: "32px",
  textAlign: "center",
};

const emptyText = { color: "#475569", fontSize: "14px" };

const getEstadoStyle = (status) => {
  const base = {
    padding: "3px 10px",
    borderRadius: "20px",
    fontSize: "12px",
    fontWeight: "500",
    width: "fit-content",
  };
  if (status === "COMPLETADO") return { ...base, background: "#052e16", color: "#22c55e" };
  if (status === "ERROR")      return { ...base, background: "#2b0a0a", color: "#ef4444" };
  return                              { ...base, background: "#3b2f0a", color: "#f59e0b" };
};

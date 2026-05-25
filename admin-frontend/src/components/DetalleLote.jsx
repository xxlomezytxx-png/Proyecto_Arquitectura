import React, { useEffect } from "react";

const DetalleLote = ({ lote, cerrar }) => {

  useEffect(() => {
    const esc = (e) => e.key === "Escape" && cerrar();
    window.addEventListener("keydown", esc);
    return () => window.removeEventListener("keydown", esc);
  }, [cerrar]);

  if (!lote) return null;

  return (
    <div style={overlay} onClick={cerrar}>
      <div style={modal} onClick={(e) => e.stopPropagation()}>

        {/* HEADER */}
        <div style={header}>
          <div>
            <h2 style={title}>Detalle del Lote</h2>
            <p style={subtitle}>Información del procesamiento</p>
          </div>

          <button style={closeButton} onClick={cerrar}>
            ✕
          </button>
        </div>

        {/* BODY */}
        <div style={body}>

          <div style={row}>
            <span style={label}>ID</span>
            <span style={value}>{lote.id}</span>
          </div>

          <div style={row}>
            <span style={label}>Estado</span>
            <span style={estado(lote.status)}>
              {lote.status}
            </span>
          </div>

          <div style={row}>
            <span style={label}>Procesados</span>
            <span style={value}>{lote.processed_rows}</span>
          </div>

          <div style={row}>
            <span style={label}>Válidos</span>
            <span style={value}>{lote.valid_rows}</span>
          </div>

          <div style={row}>
            <span style={label}>Inválidos</span>
            <span style={value}>{lote.invalid_rows}</span>
          </div>

        </div>

        {/* FOOTER */}
        <div style={footer}>
          <button style={primaryBtn} onClick={cerrar}>
            Cerrar
          </button>
        </div>

      </div>
    </div>
  );
};

export default DetalleLote;


/* ================= ESTILOS ================= */

const overlay = {
  position: "fixed",
  top: 0,
  left: 0,
  width: "100%",
  height: "100%",
  background: "rgba(2, 6, 23, 0.8)",
  display: "flex",
  justifyContent: "center",
  alignItems: "center",
  backdropFilter: "blur(6px)"
};

const modal = {
  width: "420px",
  background: "#020617",
  border: "1px solid #1e293b",
  borderRadius: "14px",
  boxShadow: "0 20px 60px rgba(0,0,0,0.6)",
  animation: "fadeIn 0.25s ease"
};

const header = {
  display: "flex",
  justifyContent: "space-between",
  alignItems: "center",
  padding: "18px 20px",
  borderBottom: "1px solid #1e293b"
};

const title = {
  fontSize: "16px",
  margin: 0
};

const subtitle = {
  fontSize: "12px",
  color: "#64748b",
  marginTop: "3px"
};

const closeButton = {
  background: "transparent",
  border: "none",
  color: "#94a3b8",
  fontSize: "16px",
  cursor: "pointer"
};

const body = {
  padding: "20px"
};

const row = {
  display: "flex",
  justifyContent: "space-between",
  marginBottom: "14px"
};

const label = {
  fontSize: "13px",
  color: "#64748b"
};

const value = {
  fontSize: "14px",
  fontWeight: "500"
};

const footer = {
  padding: "15px 20px",
  borderTop: "1px solid #1e293b",
  display: "flex",
  justifyContent: "flex-end"
};

const primaryBtn = {
  background: "#3b82f6",
  border: "none",
  padding: "8px 16px",
  borderRadius: "6px",
  color: "white",
  cursor: "pointer"
};

const estado = (estado) => {
  const base = {
    fontSize: "12px",
    padding: "4px 10px",
    borderRadius: "20px"
  };

  if (estado === "COMPLETADO") {
    return { ...base, background: "#052e16", color: "#22c55e" };
  }

  if (estado === "ERROR") {
    return { ...base, background: "#2b0a0a", color: "#ef4444" };
  }

  return { ...base, background: "#3b2f0a", color: "#f59e0b" };
};
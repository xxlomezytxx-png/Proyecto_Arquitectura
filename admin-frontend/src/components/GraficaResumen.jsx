import React from "react";

const GraficaResumen = ({ lotes }) => {
  if (!lotes || lotes.length === 0) return null;

  const totalValidos = lotes.reduce((acc, l) => acc + l.valid_rows, 0);
  const totalInvalidos = lotes.reduce((acc, l) => acc + l.invalid_rows, 0);

  const total = totalValidos + totalInvalidos;

  const porcentajeValidos = total ? (totalValidos / total) * 100 : 0;
  const porcentajeInvalidos = total ? (totalInvalidos / total) * 100 : 0;

  return (
    <div style={container}>
      <h3 style={titulo}>Resumen de Registros</h3>

      {/* Barra Válidos */}
      <div style={fila}>
        <span style={label}>Válidos</span>
        <div style={barraContainer}>
          <div
            style={{
              ...barra,
              width: `${porcentajeValidos}%`,
              background: "#22c55e"
            }}
          />
        </div>
        <span style={valor}>{totalValidos}</span>
      </div>

      {/* Barra Inválidos */}
      <div style={fila}>
        <span style={label}>Inválidos</span>
        <div style={barraContainer}>
          <div
            style={{
              ...barra,
              width: `${porcentajeInvalidos}%`,
              background: "#ef4444"
            }}
          />
        </div>
        <span style={valor}>{totalInvalidos}</span>
      </div>
    </div>
  );
};

export default GraficaResumen;


/* ================== ESTILOS ================== */

const container = {
  background: "#020617",
  border: "1px solid #1e293b",
  padding: "20px",
  borderRadius: "10px",
  marginTop: "20px"
};

const titulo = {
  marginBottom: "15px",
  fontSize: "16px",
  color: "#e2e8f0"
};

const fila = {
  display: "flex",
  alignItems: "center",
  marginBottom: "10px"
};

const label = {
  width: "80px",
  fontSize: "14px"
};

const barraContainer = {
  flex: 1,
  height: "10px",
  background: "#1e293b",
  borderRadius: "5px",
  margin: "0 10px"
};

const barra = {
  height: "100%",
  borderRadius: "5px"
};

const valor = {
  width: "50px",
  textAlign: "right"
};
import React from "react";

const normalizar = (s) => String(s || "").toLowerCase();

const Resumen = ({ lotes }) => {
  const total = lotes.length;
  const totalValidos = lotes.reduce((acc, l) => acc + Number(l.valid_rows || 0), 0);
  const totalInvalidos = lotes.reduce((acc, l) => acc + Number(l.invalid_rows || 0), 0);
  const completados = lotes.filter(l => normalizar(l.status) === "completed").length;

  return (
    <div style={container}>
      <Card titulo="Total de Lotes" valor={total} />
      <Card titulo="Lotes Completados" valor={completados} />
      <Card titulo="Registros Válidos" valor={totalValidos} />
      <Card titulo="Registros con Error" valor={totalInvalidos} />
    </div>
  );
};

const Card = ({ titulo, valor }) => (
  <div style={card}>
    <p style={cardTitle}>{titulo}</p>
    <h2 style={cardValue}>{valor}</h2>
  </div>
);

export default Resumen;

const container = {
  display: "grid",
  gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))",
  gap: "20px",
  marginBottom: "25px"
};

const card = {
  background: "#020617",
  border: "1px solid #1e293b",
  padding: "20px",
  borderRadius: "12px",
  boxShadow: "0 4px 20px rgba(0,0,0,0.3)"
};

const cardTitle = {
  fontSize: "13px",
  color: "#94a3b8",
  marginBottom: "8px"
};

const cardValue = {
  fontSize: "28px",
  fontWeight: "600",
  color: "#e2e8f0",
  margin: 0
};
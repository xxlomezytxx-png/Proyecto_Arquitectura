import React, { useEffect, useState } from "react";
import { getLotes } from "../services/inventoryService";
import TablaLotes from "../components/TablaLotes";
import Filtros from "../components/Filtros";
import DetalleLote from "../components/DetalleLote";
import Resumen from "../components/Resumen";
import GraficaResumen from "../components/GraficaResumen";

const AdminPage = () => {
  const [lotes, setLotes] = useState([]);
  const [filtroEstado, setFiltroEstado] = useState("");
  const [loteSeleccionado, setLoteSeleccionado] = useState(null);
  const [busqueda, setBusqueda] = useState("");
  const [pagina, setPagina] = useState(1);

  const lotesPorPagina = 5;

  useEffect(() => {
    getLotes().then(setLotes);
  }, []);

  const filtrados = lotes.filter((l) => {
    const coincideEstado =
      filtroEstado === "" || l.estado === filtroEstado;

    const coincideBusqueda =
      l.estado.toLowerCase().includes(busqueda.toLowerCase()) ||
      l.id.toString().includes(busqueda);

    return coincideEstado && coincideBusqueda;
  });

  const inicio = (pagina - 1) * lotesPorPagina;
  const fin = inicio + lotesPorPagina;
  const paginados = filtrados.slice(inicio, fin);

  const totalPaginas = Math.ceil(filtrados.length / lotesPorPagina);

  return (
    <div style={layout}>

      {/* SIDEBAR */}
      <aside style={sidebar}>
        <h2 style={logo}>TechFlow</h2>
        <p style={menu}>Dashboard</p>
        <p style={menu}>Inventario</p>
        <p style={menu}>Reportes</p>
      </aside>

      {/* CONTENIDO */}
      <main style={main}>
        
        {/* HEADER */}
        <div style={header}>
          <h1 style={title}>Panel de Inventario</h1>
          <p style={subtitle}>
            Monitoreo y control de cargas de datos
          </p>
        </div>

        {/* KPI */}
        <Resumen lotes={lotes} />

        {/* GRÁFICA */}
        <GraficaResumen lotes={lotes} />

        {/* BUSCADOR */}
        <input
          type="text"
          placeholder="Buscar registros..."
          value={busqueda}
          onChange={(e) => {
            setBusqueda(e.target.value);
            setPagina(1);
          }}
          style={input}
        />

        {/* FILTROS */}
        <Filtros setFiltroEstado={setFiltroEstado} />

        {/* TABLA */}
        <TablaLotes lotes={paginados} onSelect={setLoteSeleccionado} />

        {/* PAGINACIÓN */}
        <div style={paginacion}>
          <button disabled={pagina === 1} onClick={() => setPagina(pagina - 1)}>
            Anterior
          </button>

          <span>Página {pagina} de {totalPaginas || 1}</span>

          <button
            disabled={pagina === totalPaginas}
            onClick={() => setPagina(pagina + 1)}
          >
            Siguiente
          </button>
        </div>

      </main>

      {/* MODAL */}
      <DetalleLote
        lote={loteSeleccionado}
        cerrar={() => setLoteSeleccionado(null)}
      />

    </div>
  );
};

export default AdminPage;


/* ================= ESTILOS ================= */

const layout = {
  display: "flex",
  height: "100vh",
  background: "#020617"
};

const sidebar = {
  width: "220px",
  background: "#020617",
  borderRight: "1px solid #1e293b",
  padding: "20px"
};

const logo = {
  marginBottom: "30px",
  fontSize: "18px",
  fontWeight: "600"
};

const menu = {
  marginBottom: "15px",
  color: "#94a3b8",
  cursor: "pointer"
};

const main = {
  flex: 1,
  padding: "30px",
  overflowY: "auto"
};

const header = {
  marginBottom: "25px"
};

const title = {
  fontSize: "22px",
  margin: 0
};

const subtitle = {
  color: "#64748b",
  marginTop: "5px"
};

const input = {
  width: "100%",
  padding: "10px",
  marginBottom: "15px",
  background: "#020617",
  border: "1px solid #1e293b",
  borderRadius: "6px",
  color: "white"
};

const paginacion = {
  marginTop: "15px",
  display: "flex",
  justifyContent: "center",
  gap: "10px"
};
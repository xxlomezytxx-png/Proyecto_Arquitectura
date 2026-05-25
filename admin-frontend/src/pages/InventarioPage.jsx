import React, { useCallback, useEffect, useRef, useState } from 'react';
import { getLotes, uploadInventory } from '../services/inventoryService';
import TablaLotes from '../components/TablaLotes';
import Filtros from '../components/Filtros';
import DetalleLote from '../components/DetalleLote';
import Resumen from '../components/Resumen';
import GraficaResumen from '../components/GraficaResumen';

const InventarioPage = () => {
  const [lotes, setLotes] = useState([]);
  const [cargando, setCargando] = useState(true);
  const [error, setError] = useState(null);
  const [filtroEstado, setFiltroEstado] = useState('');
  const [loteSeleccionado, setLoteSeleccionado] = useState(null);
  const [busqueda, setBusqueda] = useState('');
  const [pagina, setPagina] = useState(1);
  const [subiendo, setSubiendo] = useState(false);
  const [toastMsg, setToastMsg] = useState(null);
  const fileInputRef = useRef(null);

  const lotesPorPagina = 5;

  const cargarLotes = useCallback(async () => {
    setCargando(true);
    setError(null);
    try {
      const data = await getLotes();
      setLotes(Array.isArray(data) ? data : []);
    } catch (e) {
      setError(e.message);
      setLotes([]);
    } finally {
      setCargando(false);
    }
  }, []);

  useEffect(() => { cargarLotes(); }, [cargarLotes]);

  const mostrarToast = (msg, tipo = 'ok') => {
    setToastMsg({ msg, tipo });
    setTimeout(() => setToastMsg(null), 3500);
  };

  const handleUpload = async (e) => {
    const file = e.target.files?.[0];
    if (!file) return;
    setSubiendo(true);
    try {
      await uploadInventory(file);
      mostrarToast(`Archivo "${file.name}" procesado correctamente.`, 'ok');
      cargarLotes();
    } catch (err) {
      mostrarToast(`Error al subir: ${err.message}`, 'error');
    } finally {
      setSubiendo(false);
      e.target.value = '';
    }
  };

  const filtrados = lotes.filter((l) => {
    const coincideEstado = filtroEstado === '' || l.status === filtroEstado;
    const coincideBusqueda =
      (l.status || '').toLowerCase().includes(busqueda.toLowerCase()) ||
      (l.file_name || '').toLowerCase().includes(busqueda.toLowerCase()) ||
      l.id.toString().includes(busqueda);
    return coincideEstado && coincideBusqueda;
  });

  const inicio = (pagina - 1) * lotesPorPagina;
  const paginados = filtrados.slice(inicio, inicio + lotesPorPagina);
  const totalPaginas = Math.ceil(filtrados.length / lotesPorPagina);

  return (
    <div style={page}>

      {/* Toast */}
      {toastMsg && (
        <div style={toast(toastMsg.tipo)}>
          {toastMsg.tipo === 'ok' ? '✓' : '✗'} {toastMsg.msg}
        </div>
      )}

      {/* Header */}
      <div style={headerWrap}>
        <div>
          <h1 style={titleStyle}>Panel de Inventario</h1>
          <p style={subtitle}>Monitoreo y control de cargas de datos</p>
        </div>
        <div style={headerActions}>
          <button
            style={reloadBtn}
            onClick={cargarLotes}
            disabled={cargando}
            title="Actualizar"
          >
            {cargando ? '...' : '↺ Actualizar'}
          </button>
          <button
            style={uploadBtn}
            onClick={() => fileInputRef.current?.click()}
            disabled={subiendo}
          >
            {subiendo ? 'Procesando...' : '↑ Subir archivo'}
          </button>
          <input
            ref={fileInputRef}
            type="file"
            accept=".csv,.xlsx,.xls"
            style={{ display: 'none' }}
            onChange={handleUpload}
          />
        </div>
      </div>

      {/* Error */}
      {error && (
        <div style={errorBanner}>
          ⚠ No se pudo conectar con el servicio de inventario: {error}
        </div>
      )}

      {/* KPI */}
      <Resumen lotes={lotes} />

      {/* Gráfica */}
      <GraficaResumen lotes={lotes} />

      {/* Buscador */}
      <input
        type="text"
        placeholder="Buscar por ID, nombre de archivo o estado..."
        value={busqueda}
        onChange={(e) => { setBusqueda(e.target.value); setPagina(1); }}
        style={searchInput}
      />

      {/* Filtros */}
      <Filtros setFiltroEstado={(v) => { setFiltroEstado(v); setPagina(1); }} filtroActual={filtroEstado} />

      {/* Tabla */}
      {cargando ? (
        <div style={loadingWrap}>
          <p style={loadingText}>Cargando lotes...</p>
        </div>
      ) : (
        <TablaLotes lotes={paginados} onSelect={setLoteSeleccionado} />
      )}

      {/* Paginación */}
      {!cargando && filtrados.length > 0 && (
        <div style={paginacion}>
          <button disabled={pagina === 1} onClick={() => setPagina(pagina - 1)}>
            Anterior
          </button>
          <span style={paginaLabel}>Página {pagina} de {totalPaginas || 1}</span>
          <button
            disabled={pagina >= totalPaginas}
            onClick={() => setPagina(pagina + 1)}
          >
            Siguiente
          </button>
        </div>
      )}

      {/* Modal */}
      <DetalleLote
        lote={loteSeleccionado}
        cerrar={() => setLoteSeleccionado(null)}
      />
    </div>
  );
};

export default InventarioPage;


/* ================= ESTILOS ================= */

const page = { padding: '30px', overflowY: 'auto', flex: 1, position: 'relative', background: '#0f172a' };

const headerWrap = {
  display: 'flex',
  justifyContent: 'space-between',
  alignItems: 'flex-start',
  marginBottom: '28px',
  gap: '16px',
  flexWrap: 'wrap',
};

const titleStyle = { fontSize: '22px', margin: 0, color: '#e2e8f0' };
const subtitle = { color: '#64748b', marginTop: '5px', fontSize: '14px' };

const headerActions = { display: 'flex', gap: '10px', alignItems: 'center' };

const reloadBtn = {
  background: 'transparent',
  border: '1px solid #1e293b',
  color: '#94a3b8',
  padding: '9px 14px',
  borderRadius: '8px',
  fontSize: '13px',
  cursor: 'pointer',
};

const uploadBtn = {
  background: '#3b82f6',
  border: 'none',
  color: '#fff',
  padding: '9px 16px',
  borderRadius: '8px',
  fontSize: '13px',
  cursor: 'pointer',
  fontWeight: '500',
};

const errorBanner = {
  background: '#2b0a0a',
  border: '1px solid #7f1d1d',
  color: '#fca5a5',
  padding: '12px 16px',
  borderRadius: '8px',
  fontSize: '13px',
  marginBottom: '20px',
};

const searchInput = {
  width: '100%',
  padding: '10px 14px',
  marginBottom: '14px',
  background: '#020617',
  border: '1px solid #1e293b',
  borderRadius: '8px',
  color: '#e2e8f0',
  fontSize: '14px',
  outline: 'none',
};

const loadingWrap = {
  background: '#020617',
  border: '1px solid #1e293b',
  borderRadius: '12px',
  padding: '40px',
  textAlign: 'center',
  marginTop: '20px',
};

const loadingText = { color: '#475569', fontSize: '14px' };

const paginacion = {
  marginTop: '16px',
  display: 'flex',
  justifyContent: 'center',
  alignItems: 'center',
  gap: '14px',
};

const paginaLabel = { fontSize: '13px', color: '#94a3b8' };

const toast = (tipo) => ({
  position: 'fixed',
  bottom: '24px',
  right: '24px',
  background: tipo === 'ok' ? '#052e16' : '#2b0a0a',
  border: `1px solid ${tipo === 'ok' ? '#22c55e' : '#ef4444'}`,
  color: tipo === 'ok' ? '#22c55e' : '#ef4444',
  padding: '12px 18px',
  borderRadius: '10px',
  fontSize: '13px',
  zIndex: 9999,
  boxShadow: '0 4px 20px rgba(0,0,0,0.5)',
  animation: 'fadeIn 0.2s ease',
});

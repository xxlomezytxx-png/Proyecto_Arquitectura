import React, { useEffect, useState } from 'react';
import { getServicesHealth } from '../services/systemService';
import { getLotes } from '../services/inventoryService';
import { Boxes, SlidersHorizontal, Tag, Sparkles, ExternalLink } from 'lucide-react';

const DashboardPage = ({ onNavegar }) => {
  const [servicios, setServicios] = useState([]);
  const [lotes, setLotes] = useState([]);
  const [cargandoServicios, setCargandoServicios] = useState(true);
  const [cargandoLotes, setCargandoLotes] = useState(true);
  const [errorServicios, setErrorServicios] = useState(null);
  const [errorLotes, setErrorLotes] = useState(null);

  useEffect(() => {
    let activo = true;

    async function cargar() {
      try {
        const svcs = await getServicesHealth();
        if (activo) setServicios(svcs);
      } catch (e) {
        if (activo) {
          setServicios([]);
          setErrorServicios(e?.message || "Error al cargar servicios");
        }
      } finally {
        if (activo) setCargandoServicios(false);
      }
    }

    async function cargarLotes() {
      try {
        const data = await getLotes();
        if (activo) setLotes(Array.isArray(data) ? data : []);
      } catch (e) {
        if (activo) {
          setLotes([]);
          setErrorLotes(e?.message || "Error al cargar lotes");
        }
      } finally {
        if (activo) setCargandoLotes(false);
      }
    }

    cargar();
    cargarLotes();

    return () => { activo = false; };
  }, []);

  const totalValidos   = lotes.reduce((s, l) => s + (l.valid_rows   || 0), 0);
  const totalInvalidos = lotes.reduce((s, l) => s + (l.invalid_rows || 0), 0);
  const ultimosLotes   = [...lotes].slice(-3).reverse();
  const serviciosOnline = servicios.filter(s => s.status === 'online').length;

  return (
    <div className="px-7 py-6">
      {/* KPIs */}
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-4">
        <KpiCard label="Total de Lotes"      value={lotes.length}    loading={cargandoLotes}    tone="neutral" />
        <KpiCard label="Registros Válidos"   value={totalValidos}    loading={cargandoLotes}    tone="success" />
        <KpiCard label="Registros Inválidos" value={totalInvalidos}  loading={cargandoLotes}    tone="danger"  />
        <KpiCard
          label="Servicios Activos"
          value={cargandoServicios ? null : `${serviciosOnline} / ${servicios.length}`}
          loading={cargandoServicios}
          tone="ai"
        />
      </div>

      {/* Estado de servicios */}
      <section className="mt-6">
        <div className="mb-3 flex items-center justify-between">
          <h2 className="text-[15px] font-semibold tracking-tight text-[#f1f5f9]">Estado de Servicios</h2>
          {cargandoServicios && (
            <span className="rounded-full bg-[#1e293b] px-2.5 py-0.5 text-[11.5px] text-[#94a3b8]">
              Verificando…
            </span>
          )}
        </div>
        {errorServicios && (
          <div className="mb-3 rounded-lg bg-rose-900/40 border border-rose-700 px-4 py-2 text-sm text-rose-400">
            {errorServicios}
          </div>
        )}
        <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
          {cargandoServicios
            ? Array(7).fill(0).map((_, i) => <ServiceCardSkeleton key={i} />)
            : servicios.map((svc) => <ServiceCard key={svc.key} svc={svc} />)}
        </div>
      </section>

      {/* Lotes recientes */}
      <section className="mt-6">
        <div className="mb-3 flex items-center justify-between">
          <h2 className="text-[15px] font-semibold tracking-tight text-[#f1f5f9]">Lotes Recientes</h2>
          <button
            type="button"
            onClick={() => onNavegar('inventario')}
            className="text-[12.5px] text-[#60a5fa] transition hover:text-[#f1f5f9]"
          >
            Ver todos →
          </button>
        </div>
        {errorLotes && (
          <div className="mb-3 rounded-lg bg-rose-900/40 border border-rose-700 px-4 py-2 text-sm text-rose-400">
            {errorLotes}
          </div>
        )}
        <div className="overflow-hidden rounded-2xl bg-[#1e293b] ring-1 ring-[#334155]">
          {cargandoLotes ? (
            <div className="px-5 py-4 text-[13px] text-[#94a3b8]">Cargando lotes…</div>
          ) : ultimosLotes.length === 0 ? (
            <div className="px-5 py-4 text-[13px] text-[#94a3b8]">No hay lotes registrados aún.</div>
          ) : (
            ultimosLotes.map((l, i) => (
              <div
                key={l.id}
                className={`flex items-center justify-between px-5 py-3.5 ${
                  i < ultimosLotes.length - 1 ? 'border-b border-[#334155]' : ''
                }`}
              >
                <div>
                  <span className="text-[13.5px] font-medium text-[#f1f5f9]">Lote #{l.id}</span>
                  {l.file_name && (
                    <span className="ml-2 text-[12px] text-[#94a3b8]">{l.file_name}</span>
                  )}
                </div>
                <div className="flex items-center gap-4">
                  <span className="num text-[12.5px] text-[#94a3b8]">
                    {l.valid_rows} válidos · {l.invalid_rows} inválidos
                  </span>
                  <LoteBadge status={l.status} />
                </div>
              </div>
            ))
          )}
        </div>
      </section>

      {/* Accesos rápidos */}
      <section className="mt-6">
        <h2 className="mb-3 text-[15px] font-semibold tracking-tight text-[#f1f5f9]">Accesos Rápidos</h2>
        <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 xl:grid-cols-4">
          <QuickCard
            icon={Boxes}
            titulo="Gestionar Inventario"
            desc="Ver lotes, subir archivos y revisar errores"
            onClick={() => onNavegar('inventario')}
          />
          <QuickCard
            icon={SlidersHorizontal}
            titulo="Ver Reportes"
            desc="Estadísticas y análisis de los datos cargados"
            onClick={() => onNavegar('reportes')}
          />
          <QuickCard
            icon={Tag}
            titulo="Precios IA"
            desc="Revisar y recalcular precios sugeridos"
            onClick={() => onNavegar('precios')}
            ai
          />
          <QuickCard
            icon={ExternalLink}
            titulo="Ver Tienda"
            desc="Abrir el catálogo comercial en una nueva pestaña"
            href="http://localhost:3000"
          />
        </div>
      </section>
    </div>
  );
};

/* ── Sub-componentes ── */

const TONE = {
  neutral: { value: 'text-[#f1f5f9]'    },
  success: { value: 'text-emerald-400'   },
  danger:  { value: 'text-rose-400'      },
  ai:      { value: 'text-amber-400'     },
};

const KpiCard = ({ label, value, loading, tone = 'neutral' }) => {
  const t = TONE[tone] ?? TONE.neutral;
  return (
    <div className="relative overflow-hidden rounded-2xl bg-[#1e293b] p-5 ring-1 ring-[#334155]">
      {tone === 'ai' && (
        <div
          className="pointer-events-none absolute -right-6 -top-6 h-24 w-24 rounded-full"
          style={{ background: 'radial-gradient(closest-side, rgba(251,191,36,.35), transparent 70%)' }}
        />
      )}
      <div className="relative">
        <div className="flex items-center gap-1 text-[11px] uppercase tracking-[.14em] text-[#94a3b8]">
          {tone === 'ai' && <Sparkles size={11} className="text-amber-400" />}
          {label}
        </div>
        {loading ? (
          <div className="mt-3 h-8 w-24 animate-pulse rounded-lg bg-[#334155]" />
        ) : (
          <div className={`num mt-2 text-[32px] font-semibold tracking-tight ${t.value}`}>
            {typeof value === 'number' && value > 999
              ? value.toLocaleString('es-ES')
              : (value ?? '—')}
          </div>
        )}
      </div>
    </div>
  );
};

const ServiceCard = ({ svc }) => {
  const isOnline   = svc.status === 'online';
  const isDegraded = svc.status === 'degraded';
  const dotCls = isOnline
    ? 'bg-emerald-500 shadow-[0_0_6px_rgba(34,197,94,.5)]'
    : isDegraded ? 'bg-amber-400' : 'bg-rose-500';
  const statusText  = isOnline ? 'En línea' : isDegraded ? 'Degradado' : 'Fuera de línea';
  const statusColor = isOnline ? 'text-emerald-400' : isDegraded ? 'text-amber-400' : 'text-rose-400';
  return (
    <div className="flex items-center gap-3 rounded-xl bg-[#1e293b] p-3.5 ring-1 ring-[#334155]">
      <div className={`h-2.5 w-2.5 shrink-0 rounded-full ${dotCls}`} />
      <div>
        <p className="text-[13px] font-medium text-[#f1f5f9]">{svc.name}</p>
        <p className={`text-[11px] ${statusColor}`}>{statusText}</p>
      </div>
    </div>
  );
};

const ServiceCardSkeleton = () => (
  <div className="flex items-center gap-3 rounded-xl bg-[#1e293b] p-3.5 ring-1 ring-[#334155]">
    <div className="h-2.5 w-2.5 shrink-0 animate-pulse rounded-full bg-[#334155]" />
    <div className="flex-1">
      <div className="h-3 w-28 animate-pulse rounded bg-[#334155]" />
      <div className="mt-1.5 h-2.5 w-16 animate-pulse rounded bg-[#334155]" />
    </div>
  </div>
);

const LoteBadge = ({ status }) => {
  if (status === 'COMPLETADO') return (
    <span className="inline-flex items-center rounded-full px-2.5 py-0.5 text-[11px] font-medium ring-1"
      style={{ background: '#052e16', color: '#22c55e', borderColor: '#166534' }}>
      {status}
    </span>
  );
  if (status === 'ERROR') return (
    <span className="inline-flex items-center rounded-full px-2.5 py-0.5 text-[11px] font-medium ring-1"
      style={{ background: '#2b0a0a', color: '#ef4444', borderColor: '#7f1d1d' }}>
      {status}
    </span>
  );
  return (
    <span className="inline-flex items-center rounded-full px-2.5 py-0.5 text-[11px] font-medium ring-1"
      style={{ background: '#3b2f0a', color: '#f59e0b', borderColor: '#92400e' }}>
      {status}
    </span>
  );
};

const QuickCard = ({ icon: Icon, titulo, desc, onClick, href, ai }) => {
  const cardCls = "flex w-full items-start gap-3 rounded-xl bg-[#1e293b] p-4 text-left ring-1 ring-[#334155] transition hover:ring-[#60a5fa] hover:bg-[#1e3a5f]";
  const iconCls = ai
    ? 'grid h-9 w-9 shrink-0 place-items-center rounded-xl bg-amber-400/15 text-amber-400'
    : 'grid h-9 w-9 shrink-0 place-items-center rounded-xl bg-[#334155] text-[#94a3b8]';
  const inner = (
    <>
      <div className={iconCls}>
        <Icon size={16} strokeWidth={1.8} />
      </div>
      <div>
        <p className="text-[13.5px] font-semibold text-[#f1f5f9]">{titulo}</p>
        <p className="mt-0.5 text-[12px] text-[#94a3b8]">{desc}</p>
      </div>
    </>
  );
  if (href) {
    return (
      <a href={href} target="_blank" rel="noreferrer" className={`${cardCls} no-underline`}>
        {inner}
      </a>
    );
  }
  return (
    <button type="button" onClick={onClick} className={cardCls}>
      {inner}
    </button>
  );
};

export default DashboardPage;

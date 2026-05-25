import { useEffect, useState } from "react";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
} from "recharts";
import api from "../services/api";

interface PricePoint {
  fecha: string;
  precio: number;
}

interface PricingDecision {
  id: string;
  book_reference: string;
  suggested_price: number;
  created_at: string;
}

const ReportesPage = () => {
  const [data, setData] = useState<PricePoint[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    api.get("/admin/pricing")
      .then((decisions: PricingDecision[]) => {
        const points: PricePoint[] = (Array.isArray(decisions) ? decisions : [])
          .map((d) => ({
            fecha: d.created_at ? d.created_at.slice(0, 10) : "—",
            precio: d.suggested_price,
          }))
          .reverse();
        setData(points);
      })
      .catch((e: unknown) => {
        setError(e instanceof Error ? e.message : "Error al cargar datos");
      })
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="p-6 space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-white">Reportes</h1>
        <p className="text-slate-400 text-sm mt-1">Historial de precios calculados por el motor de IA</p>
      </div>

      {loading && (
        <div className="flex items-center gap-2 text-slate-400 text-sm">
          <span className="animate-spin">⟳</span> Cargando datos…
        </div>
      )}

      {error && (
        <div className="rounded-lg bg-rose-900/40 border border-rose-700 px-4 py-3 text-sm text-rose-400">
          {error}
        </div>
      )}

      {!loading && !error && data.length === 0 && (
        <div className="flex flex-col items-center justify-center py-20 text-slate-500">
          <span className="text-5xl mb-4">📊</span>
          <p className="text-lg font-medium text-slate-400">Sin datos de historial</p>
          <p className="text-sm mt-1 text-center">
            Recalcula precios desde el panel de <strong className="text-slate-300">Precios IA</strong> para ver reportes aquí.
          </p>
        </div>
      )}

      {!loading && !error && data.length > 0 && (
        <div className="bg-slate-800 rounded-xl p-4 border border-slate-700">
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={data}>
              <XAxis dataKey="fecha" stroke="#94a3b8" tick={{ fill: "#94a3b8", fontSize: 12 }} />
              <YAxis stroke="#94a3b8" tick={{ fill: "#94a3b8", fontSize: 12 }} />
              <Tooltip
                contentStyle={{ backgroundColor: "#1e293b", border: "1px solid #334155", borderRadius: 8 }}
                labelStyle={{ color: "#f1f5f9" }}
                itemStyle={{ color: "#60a5fa" }}
              />
              <Line dataKey="precio" stroke="#2563eb" strokeWidth={2} dot={false} />
            </LineChart>
          </ResponsiveContainer>
        </div>
      )}
    </div>
  );
};

export default ReportesPage;

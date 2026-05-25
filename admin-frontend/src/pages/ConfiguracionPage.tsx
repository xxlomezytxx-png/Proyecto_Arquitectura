import { useState, useEffect } from "react";
import api from "../services/api";

const ConfiguracionPage = () => {
  const [min, setMin] = useState(40000);
  const [max, setMax] = useState(80000);
  const [saving, setSaving] = useState(false);
  const [saved, setSaved] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    api.get("/config").then((data: Record<string, unknown>) => {
      if (data.minPrice !== undefined) setMin(Number(data.minPrice));
      if (data.maxPrice !== undefined) setMax(Number(data.maxPrice));
    }).catch((e: unknown) => {
      setError(e instanceof Error ? e.message : "Error al cargar configuración");
    });
  }, []);

  const save = async () => {
    setSaving(true);
    setSaved(false);
    setError(null);
    try {
      await Promise.all([
        api.put("/config/minPrice", { value: min }),
        api.put("/config/maxPrice", { value: max }),
      ]);
      setSaved(true);
      setTimeout(() => setSaved(false), 3000);
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "Error al guardar");
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="p-6 space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-white">Configuración</h1>
        <p className="text-slate-400 text-sm mt-1">Parámetros del motor de precios</p>
      </div>

      <div className="bg-slate-800 rounded-xl p-6 border border-slate-700 max-w-md space-y-5">
        <div className="space-y-1">
          <label className="text-sm font-medium text-slate-300">Precio mínimo</label>
          <input
            type="number"
            value={min}
            onChange={(e) => setMin(Number(e.target.value))}
            className="w-full bg-slate-900 border border-slate-600 text-white rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>

        <div className="space-y-1">
          <label className="text-sm font-medium text-slate-300">Precio máximo</label>
          <input
            type="number"
            value={max}
            onChange={(e) => setMax(Number(e.target.value))}
            className="w-full bg-slate-900 border border-slate-600 text-white rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>

        {saved && (
          <div className="rounded-lg bg-emerald-900/40 border border-emerald-700 px-3 py-2 text-sm text-emerald-400">
            Configuración guardada correctamente.
          </div>
        )}
        {error && (
          <div className="rounded-lg bg-rose-900/40 border border-rose-700 px-3 py-2 text-sm text-rose-400">
            {error}
          </div>
        )}

        <button
          onClick={save}
          disabled={saving}
          className="w-full bg-blue-600 hover:bg-blue-700 disabled:opacity-50 text-white font-medium py-2 rounded-lg transition-colors"
        >
          {saving ? "Guardando…" : "Guardar configuración"}
        </button>
      </div>
    </div>
  );
};

export default ConfiguracionPage;

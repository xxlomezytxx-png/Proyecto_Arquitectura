import { Fragment, useEffect, useState } from "react";
import { authAxios } from "../services/authClient";
import {
  getLocalOrders,
  localOrdersToAuditEntries,
} from "../orders/orders.storage";

const BFF_URL = import.meta.env.VITE_BFF_URL || "http://localhost:8009";

type Tab = "pricing" | "orders" | "enrichment";

interface AuditEntry {
  id: string;
  entity_type: string;
  entity_id: string;
  action: string;
  service_name: string;
  input_data: unknown;
  output_data: unknown;
  timestamp: string;
}

interface ExpandedRows {
  [id: string]: boolean;
}

async function fetchAudit(tab: Tab): Promise<AuditEntry[]> {
  const path = tab === "pricing" ? "pricing" : tab === "orders" ? "orders" : "enrichment";
  const res = await authAxios.get(`${BFF_URL}/api/admin/audit/${path}`);
  return Array.isArray(res.data) ? res.data : [];
}

function formatTs(ts: string): string {
  return new Date(ts).toLocaleString("es-CO", {
    dateStyle: "short",
    timeStyle: "short",
  });
}

function JsonCell({ raw }: { raw: unknown }) {
  if (raw === null || raw === undefined) {
    return <span style={{ fontSize: 12, color: "#94a3b8" }}>—</span>;
  }
  if (typeof raw === "string") {
    try {
      const parsed = JSON.parse(raw);
      return <pre style={{ margin: 0, fontSize: 11, whiteSpace: "pre-wrap", color: "#e2e8f0" }}>{JSON.stringify(parsed, null, 2)}</pre>;
    } catch {
      return <span style={{ fontSize: 12, color: "#e2e8f0" }}>{raw}</span>;
    }
  }
  return <pre style={{ margin: 0, fontSize: 11, whiteSpace: "pre-wrap", color: "#e2e8f0" }}>{JSON.stringify(raw, null, 2)}</pre>;
}

function formatProducts(raw: unknown): string {
  if (!raw) return "—";

  let products: any[] = []

  if (typeof raw === "string") {
    try {
      products = JSON.parse(raw)
    } catch {
      return String(raw)
    }
  } else if (Array.isArray(raw)) {
    products = raw
  } else if (typeof raw === "object") {
    products = [raw]
  }

  if (!Array.isArray(products)) {
    return String(raw)
  }

  return products
    .map((item) => {
      if (item && typeof item === "object") {
        const title = item.title || item.bookId || item.name || "Producto"
        const qty = item.quantity ?? 1
        return `${title} x${qty}`
      }
      return String(item)
    })
    .join(", ")
}

export default function AuditPage() {
  const [tab, setTab] = useState<Tab>("pricing");
  const [entries, setEntries] = useState<AuditEntry[]>([]);
  const [loading, setLoading] = useState(false);
  const [expanded, setExpanded] = useState<ExpandedRows>({});

  useEffect(() => {
    setLoading(true);
    setExpanded({});

    const localOrderEntries =
      tab === "orders"
        ? localOrdersToAuditEntries(getLocalOrders())
        : [];

    fetchAudit(tab)
      .then((remoteEntries) => {
        if (tab === "orders") {
          setEntries([...localOrderEntries, ...remoteEntries]);
        } else {
          setEntries(remoteEntries);
        }
      })
      .catch(() => {
        if (tab === "orders") {
          setEntries(localOrderEntries);
        } else {
          setEntries([]);
        }
      })
      .finally(() => setLoading(false));
  }, [tab]);

  const toggleRow = (id: string) =>
    setExpanded((prev) => ({ ...prev, [id]: !prev[id] }));

  return (
    <div style={{ padding: "28px 32px", background: "#0f172a", color: "#f1f5f9", minHeight: "100%" }}>
      <h2 style={{ marginBottom: 8, fontSize: 22, fontWeight: 700, color: "#f1f5f9" }}>Auditoría IA</h2>
      <p style={{ color: "#94a3b8", marginBottom: 24, fontSize: 14 }}>
        Registro de decisiones de pricing y pedidos procesados por el sistema.
      </p>

      <div style={{ display: "flex", gap: 8, marginBottom: 24 }}>
        {(["pricing", "orders", "enrichment"] as Tab[]).map((t) => (
          <button
            key={t}
            onClick={() => setTab(t)}
            style={{
              padding: "7px 18px",
              borderRadius: 8,
              border: "1px solid",
              borderColor: tab === t ? "#22c55e" : "#334155",
              background: tab === t ? "#052e16" : "#1e293b",
              color: tab === t ? "#22c55e" : "#94a3b8",
              fontWeight: 600,
              cursor: "pointer",
              fontSize: 14,
            }}
          >
            {t === "pricing" ? "💰 Pricing" : t === "orders" ? "📦 Pedidos" : "🔍 Enriquecimiento"}
          </button>
        ))}
      </div>

      {loading && <p style={{ color: "#94a3b8" }}>Cargando registros...</p>}

      {!loading && entries.length === 0 && (
        <p style={{ color: "#94a3b8", fontSize: 14 }}>Sin registros de auditoría.</p>
      )}

      {!loading && entries.length > 0 && (
        <div style={{ overflowX: "auto" }}>
          <table style={{ width: "100%", borderCollapse: "collapse", fontSize: 13 }}>
            <thead>
              <tr style={{ background: "#1e293b", borderBottom: "2px solid #334155" }}>
                {(tab === "orders" ? [
                  "Pedido ID",
                  "Cliente",
                  "Productos",
                  "Total",
                  "Fecha",
                  "Estado",
                  "Origen",
                ] : [
                  "Entidad ID",
                  "Acción",
                  "Servicio",
                  "Timestamp",
                  "",
                ]).map((h) => (
                  <th key={h} style={{ padding: "10px 12px", textAlign: "left", fontWeight: 600, color: "#94a3b8" }}>
                    {h}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {entries.map((entry) => (
                <Fragment key={entry.id}>
                  <tr style={{ borderBottom: "1px solid #1e293b", background: "#0f172a" }}>
                    {tab === "orders" ? (
                      <>
                        <td style={{ padding: "10px 12px", fontFamily: "monospace", color: "#e2e8f0" }}>{entry.output_data?.id || entry.entity_id}</td>
                        <td style={{ padding: "10px 12px", color: "#f1f5f9" }}>{entry.output_data?.customer?.name || "Cliente no disponible"}</td>
                        <td style={{ padding: "10px 12px", color: "#94a3b8" }}>{(entry.output_data?.products || entry.output_data?.items || []).map((p) => p.name).join(', ') || "N/A"}</td>
                        <td style={{ padding: "10px 12px", color: "#e2e8f0" }}>{entry.output_data?.total || "—"}</td>
                        <td style={{ padding: "10px 12px", color: "#94a3b8" }}>{formatTs(entry.output_data?.createdAt || entry.timestamp)}</td>
                        <td style={{ padding: "10px 12px", color: "#22c55e" }}>{entry.output_data?.status || entry.action}</td>
                        <td style={{ padding: "10px 12px", color: "#94a3b8" }}>{entry.service_name}</td>
                      </>
                    ) : (
                      <>
                        <td style={{ padding: "10px 12px", fontFamily: "monospace", color: "#e2e8f0" }}>{entry.entity_id}</td>
                        <td style={{ padding: "10px 12px" }}>
                          <span style={{
                            background: "#052e16",
                            color: "#22c55e",
                            border: "1px solid #166534",
                            borderRadius: 6,
                            padding: "2px 8px",
                            fontSize: 12,
                            fontWeight: 600,
                          }}>
                            {entry.action}
                          </span>
                        </td>
                        <td style={{ padding: "10px 12px", color: "#94a3b8" }}>{entry.service_name}</td>
                        <td style={{ padding: "10px 12px", color: "#94a3b8" }}>{formatTs(entry.timestamp)}</td>
                        <td style={{ padding: "10px 12px" }}>
                          <button
                            onClick={() => toggleRow(entry.id)}
                            style={{
                              background: "none",
                              border: "1px solid #334155",
                              borderRadius: 6,
                              padding: "3px 10px",
                              cursor: "pointer",
                              fontSize: 12,
                              color: "#94a3b8",
                            }}
                          >
                            {expanded[entry.id] ? "▲ Cerrar" : "▼ Ver"}
                          </button>
                        </td>
                      </>
                    )}
                  </tr>

                  {expanded[entry.id] && (
                    <tr style={{ background: "#111827" }}>
                      <td colSpan={tab === "orders" ? 7 : 5} style={{ padding: "12px 16px" }}>
                        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 16 }}>
                          <div>
                            <p style={{ fontWeight: 600, marginBottom: 4, fontSize: 12, color: "#94a3b8" }}>Input</p>
                            <div style={{ background: "#1e293b", border: "1px solid #334155", borderRadius: 6, padding: 10, maxHeight: 200, overflow: "auto" }}>
                              <JsonCell raw={entry.input_data} />
                            </div>
                          </div>
                          <div>
                            <p style={{ fontWeight: 600, marginBottom: 4, fontSize: 12, color: "#94a3b8" }}>Output</p>
                            <div style={{ background: "#1e293b", border: "1px solid #334155", borderRadius: 6, padding: 10, maxHeight: 200, overflow: "auto" }}>
                              <JsonCell raw={entry.output_data} />
                            </div>
                          </div>
                        </div>
                      </td>
                    </tr>
                  )}
                </Fragment>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}

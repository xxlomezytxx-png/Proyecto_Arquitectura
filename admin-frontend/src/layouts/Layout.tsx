import { useState } from "react";
import {
  LayoutDashboard, Boxes, Tag, Sparkles, SlidersHorizontal, Settings,
  ShieldCheck, Search, Bell, HelpCircle, ChevronDown, ChevronRight,
  ExternalLink, LogOut, MessageSquare,
} from "lucide-react";
import type { LucideIcon } from "lucide-react";
import { useAuth } from "../contexts/AuthContext";
import { Wordmark, IconBtn } from "../components/ui";
import DashboardPage from "../pages/DashboardPage";
import InventarioPage from "../pages/InventarioPage";
import ReportesPage from "../pages/ReportesPage";
import ConfiguracionPage from "../pages/ConfiguracionPage";
import EnrichmentPage from "../pages/EnrichmentPage";
import PricingDashboard from "../components/pricing/PricingDashboard";
import AuditPage from "../pages/AuditPage";
import AsistentePage from "../pages/AsistentePage";

type View = "dashboard" | "inventario" | "precios" | "enriquecimiento" | "asistente" | "reportes" | "configuracion" | "auditoria";

interface NavItem {
  id: View;
  label: string;
  icon: LucideIcon;
  aiBadge?: boolean;
}

const OPERACION_ITEMS: NavItem[] = [
  { id: "dashboard",       label: "Dashboard",       icon: LayoutDashboard },
  { id: "inventario",      label: "Inventario",      icon: Boxes },
  { id: "precios",         label: "Precios IA",      icon: Tag,             aiBadge: true },
  { id: "enriquecimiento", label: "Enriquecimiento", icon: Sparkles,        aiBadge: true },
  { id: "asistente",       label: "Asistente IA",    icon: MessageSquare,   aiBadge: true },
];

const DATOS_ITEMS: NavItem[] = [
  { id: "reportes",      label: "Reportes",      icon: SlidersHorizontal },
  { id: "configuracion", label: "Configuración", icon: Settings },
  { id: "auditoria",     label: "Auditoría",     icon: ShieldCheck },
];

const VIEW_LABELS: Record<View, string> = {
  dashboard:       "Panel de control",
  inventario:      "Inventario",
  precios:         "Precios IA",
  enriquecimiento: "Enriquecimiento",
  asistente:       "Asistente IA",
  reportes:        "Reportes",
  configuracion:   "Configuración",
  auditoria:       "Auditoría",
};

const Layout = () => {
  const [view, setView] = useState<View>("dashboard");
  const { user, logout } = useAuth();

  const renderContent = () => {
    switch (view) {
      case "dashboard":        return <DashboardPage onNavegar={(v: string) => setView(v as View)} />;
      case "inventario":       return <InventarioPage />;
      case "precios":          return <PricingDashboard />;
      case "enriquecimiento":  return <EnrichmentPage />;
      case "asistente":        return <AsistentePage />;
      case "reportes":         return <ReportesPage />;
      case "configuracion":    return <ConfiguracionPage />;
      case "auditoria":        return <AuditPage />;
    }
  };

  const initials = user?.username ? user.username.slice(0, 2).toUpperCase() : "??";

  return (
    <div className="grid h-screen w-full grid-cols-[240px_1fr] bg-[#0f172a]">
      {/* Sidebar */}
      <aside className="flex h-full flex-col border-r border-[#1e293b] bg-[#0a0f1e]">
        <div className="flex items-center gap-2 px-5 py-4 border-b border-[#1e293b]">
          <Wordmark />
        </div>

        <div className="px-3 pt-3">
          <div className="mb-2 flex items-center gap-2 rounded-lg bg-[#1e293b] px-2.5 py-2 ring-1 ring-[#334155]">
            <div className="grid h-7 w-7 place-items-center rounded-md bg-[#3b82f6] text-white text-[11px] font-semibold">
              {initials}
            </div>
            <div className="min-w-0 flex-1">
              <div className="truncate text-[12.5px] font-medium text-[#f1f5f9]">{user?.username}</div>
              <div className="truncate text-[11px] text-[#94a3b8]">{user?.role}</div>
            </div>
            <ChevronDown size={14} className="text-[#64748b]" />
          </div>
        </div>

        <nav className="flex-1 overflow-y-auto px-2 py-2 scrollbar-clean">
          <div className="px-3 pt-2 pb-1 text-[10.5px] uppercase tracking-[.16em] text-[#64748b]">Operación</div>
          {OPERACION_ITEMS.map((n) => (
            <button
              key={n.id}
              type="button"
              onClick={() => setView(n.id)}
              className={`group mb-0.5 flex w-full items-center gap-2.5 rounded-lg px-3 py-2 text-[13px] transition ${
                view === n.id
                  ? "bg-[#1e3a5f] text-[#60a5fa]"
                  : "text-[#94a3b8] hover:bg-[#1e293b] hover:text-[#f1f5f9]"
              }`}
            >
              <n.icon
                size={15}
                strokeWidth={1.9}
                className={view === n.id ? "text-[#60a5fa]" : "text-[#64748b] group-hover:text-[#f1f5f9]"}
              />
              <span className="flex-1 text-left">{n.label}</span>
              {n.aiBadge && (
                <span className="inline-flex items-center rounded-full bg-amber-400/90 px-1.5 py-0.5 text-[10px] font-semibold text-[#0a0f1e] num">
                  IA
                </span>
              )}
            </button>
          ))}

          <div className="px-3 pt-5 pb-1 text-[10.5px] uppercase tracking-[.16em] text-[#64748b]">Datos</div>
          {DATOS_ITEMS.map((n) => (
            <button
              key={n.id}
              type="button"
              onClick={() => setView(n.id)}
              className={`group mb-0.5 flex w-full items-center gap-2.5 rounded-lg px-3 py-2 text-[13px] transition ${
                view === n.id
                  ? "bg-[#1e3a5f] text-[#60a5fa]"
                  : "text-[#94a3b8] hover:bg-[#1e293b] hover:text-[#f1f5f9]"
              }`}
            >
              <n.icon
                size={15}
                strokeWidth={1.9}
                className={view === n.id ? "text-[#60a5fa]" : "text-[#64748b] group-hover:text-[#f1f5f9]"}
              />
              <span className="flex-1 text-left">{n.label}</span>
            </button>
          ))}

          <div className="mt-4 px-3">
            <a
              href="http://localhost:3000"
              target="_blank"
              rel="noreferrer"
              className="flex items-center gap-2 py-1.5 text-[12.5px] text-[#94a3b8] hover:text-[#38bdf8] transition"
            >
              <ExternalLink size={14} />
              Ir a la tienda
            </a>
          </div>
        </nav>

        {/* AI credit widget */}
        <div className="relative m-3 overflow-hidden rounded-xl bg-[#0f2a4a] p-4 text-white">
          <div
            className="absolute -right-6 -top-6 h-24 w-24 rounded-full"
            style={{ background: "radial-gradient(closest-side, rgba(245,158,11,.55), transparent 70%)" }}
          />
          <div className="relative">
            <div className="inline-flex items-center gap-1 text-[10.5px] uppercase tracking-[.18em] text-amber-300">
              <Sparkles size={11} /> Crédito IA
            </div>
            <div className="mt-1 num text-[20px] font-semibold leading-tight">8,420 / 10,000</div>
            <div className="mt-2 h-1.5 overflow-hidden rounded-full bg-white/15">
              <div className="h-full bg-amber-400" style={{ width: "84%" }} />
            </div>
          </div>
        </div>

        {/* User / logout */}
        <div className="border-t border-[#1e293b] px-3 py-3">
          <div className="flex items-center gap-2">
            <div className="grid h-8 w-8 shrink-0 place-items-center rounded-full bg-[#3b82f6] text-[11px] font-semibold text-white">
              {initials}
            </div>
            <div className="min-w-0 flex-1">
              <div className="truncate text-[12.5px] font-medium text-[#f1f5f9]">{user?.username}</div>
              <div className="truncate text-[11px] text-[#94a3b8]">{user?.role}</div>
            </div>
            <button
              type="button"
              onClick={logout}
              title="Cerrar sesión"
              className="inline-flex h-8 w-8 items-center justify-center rounded-md text-[#64748b] transition hover:bg-[#1e293b] hover:text-[#f1f5f9]"
            >
              <LogOut size={14} />
            </button>
          </div>
        </div>
      </aside>

      {/* Main */}
      <div className="flex h-full min-h-0 flex-col overflow-hidden">
        {/* Header */}
        <header className="flex h-16 items-center justify-between border-b border-[#1e293b] bg-[#0f172a]/90 px-7 backdrop-blur">
          <div>
            <div className="flex items-center gap-1.5 text-[11.5px] text-[#94a3b8]">
              <span>TechFlow</span>
              <ChevronRight size={11} />
              <span>{VIEW_LABELS[view]}</span>
            </div>
            <div className="font-serif text-[22px] leading-tight tracking-tight text-[#f1f5f9]">{VIEW_LABELS[view]}</div>
          </div>
          <div className="flex items-center gap-2">
            <div className="hidden md:flex items-center rounded-lg bg-[#1e293b] ring-1 ring-[#334155] px-3 h-9 w-64">
              <Search size={14} className="mr-2 shrink-0 text-[#64748b]" />
              <input
                placeholder="Buscar…"
                className="flex-1 bg-transparent text-[13px] text-[#f1f5f9] outline-none placeholder:text-[#64748b]"
              />
            </div>
            <IconBtn icon={HelpCircle} label="Ayuda" />
            <div className="relative">
              <IconBtn icon={Bell} label="Notificaciones" />
              <span className="absolute right-1.5 top-1.5 h-1.5 w-1.5 rounded-full bg-amber-400 ring-2 ring-[#0f172a]" />
            </div>
            <div className="ml-1 grid h-9 w-9 place-items-center rounded-full bg-[#3b82f6] text-[11px] font-semibold text-white">
              {initials}
            </div>
          </div>
        </header>

        {/* Content */}
        <div className="flex-1 overflow-auto scrollbar-clean bg-[#0f172a]">
          {renderContent()}
        </div>
      </div>
    </div>
  );
};

export default Layout;

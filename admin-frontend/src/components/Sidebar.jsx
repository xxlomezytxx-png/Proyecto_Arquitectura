import React from 'react';

const NAV_ITEMS = [
  { key: 'dashboard',   label: 'Dashboard',   icon: '◈' },
  { key: 'inventario',  label: 'Inventario',  icon: '⊞' },
  { key: 'reportes',    label: 'Reportes',    icon: '◑' },
  { key: 'precios',     label: 'Precios IA',  icon: '◎' },
];

const Sidebar = ({ paginaActual, onNavegar }) => {
  return (
    <aside style={sidebar}>
      <div style={logoWrap}>
        <h2 style={logo}>TechFlow</h2>
        <p style={logoSub}>Admin Panel</p>
      </div>

      <nav style={nav}>
        {NAV_ITEMS.map((item) => (
          <button
            key={item.key}
            style={navItem(item.key === paginaActual)}
            onClick={() => onNavegar(item.key)}
          >
            <span style={iconStyle}>{item.icon}</span>
            {item.label}
          </button>
        ))}
      </nav>

      <a
        href="http://localhost:3000"
        target="_blank"
        rel="noreferrer"
        style={storeLinkStyle}
      >
        <span style={iconStyle}>⊙</span>
        Ver tienda
      </a>

      <div style={footer}>
        <div style={dot} />
        <span style={footerText}>Sistema activo</span>
      </div>
    </aside>
  );
};

export default Sidebar;


/* ================= ESTILOS ================= */

const sidebar = {
  width: '220px',
  minWidth: '220px',
  background: '#020617',
  borderRight: '1px solid #1e293b',
  padding: '24px 12px',
  display: 'flex',
  flexDirection: 'column',
  gap: '0',
};

const logoWrap = {
  padding: '0 8px 28px',
  borderBottom: '1px solid #1e293b',
  marginBottom: '20px',
};

const logo = {
  fontSize: '18px',
  fontWeight: '700',
  color: '#e2e8f0',
  margin: 0,
};

const logoSub = {
  fontSize: '11px',
  color: '#475569',
  marginTop: '3px',
};

const nav = {
  display: 'flex',
  flexDirection: 'column',
  gap: '4px',
  flex: 1,
};

const navItem = (active) => ({
  display: 'flex',
  alignItems: 'center',
  gap: '10px',
  padding: '10px 12px',
  borderRadius: '8px',
  border: 'none',
  background: active ? 'rgba(16,185,129,0.12)' : 'transparent',
  color: active ? '#10b981' : '#64748b',
  fontSize: '14px',
  fontWeight: active ? '600' : '400',
  cursor: 'pointer',
  textAlign: 'left',
  transition: 'all 0.15s ease',
  width: '100%',
});

const iconStyle = {
  fontSize: '16px',
  opacity: 0.8,
};

const footer = {
  display: 'flex',
  alignItems: 'center',
  gap: '8px',
  padding: '12px 8px 0',
  borderTop: '1px solid #1e293b',
};

const dot = {
  width: '7px',
  height: '7px',
  borderRadius: '50%',
  background: '#22c55e',
  boxShadow: '0 0 6px #22c55e',
};

const footerText = {
  fontSize: '12px',
  color: '#475569',
};

const storeLinkStyle = {
  display: 'flex',
  alignItems: 'center',
  gap: '10px',
  padding: '10px 12px',
  borderRadius: '8px',
  border: '1px solid #1e293b',
  background: 'transparent',
  color: '#38bdf8',
  fontSize: '14px',
  fontWeight: '400',
  cursor: 'pointer',
  textDecoration: 'none',
  marginBottom: '12px',
  transition: 'all 0.15s ease',
};

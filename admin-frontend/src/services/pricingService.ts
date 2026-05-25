import { authAxios } from "./authClient";

const BASE = import.meta.env.VITE_BFF_URL || "http://localhost:8009";
const API = `${BASE}/api/admin/pricing`;
const BFF = `${BASE}/api/admin`;

// 🔹 Obtener lista de libros con precios
export const getPricingList = async () => {
  const res = await authAxios.get(`${API}`);
  return res.data;
};

// 🔹 Calcular precio de todos los libros del catálogo
export const bulkCalculate = async () => {
  const res = await authAxios.post(`${BFF}/pricing/bulk-calculate`);
  return res.data;
};

// 🔹 Recalcular precio de un libro
export const recalculatePrice = async (
  book_id: string,
  book_title: string,
  condition: string,
) => {
  const res = await authAxios.post(`${API}/recalculate`, { book_id, book_title, condition });
  return res.data;
};

// 🔹 Obtener detalle + explicación por libro
export const getBookDetail = async (book_id: string) => {
  const res = await authAxios.get(`${API}/${book_id}`);
  return res.data;
};

// 🔹 Obtener historial por libro
export const getPriceHistory = async (book_id: string) => {
  const res = await authAxios.get(`${API}/${book_id}/history`);
  return res.data;
};

// 🔹 Obtener reportes globales
export const getReports = async () => {
  const res = await authAxios.get(`${API}/reports`);
  return res.data;
};

// 🔹 Catálogo completo con flags de enriquecimiento
export const getCatalogProducts = async () => {
  const res = await authAxios.get(`${BASE}/api/catalog/products`);
  return res.data;
};

// 🔹 Configuración
export const getConfig = async () => {
  const res = await authAxios.get(`${API}/config`);
  return res.data;
};

export const saveConfig = async (config: Record<string, unknown>) => {
  const res = await authAxios.post(`${API}/config`, config);
  return res.data;
};
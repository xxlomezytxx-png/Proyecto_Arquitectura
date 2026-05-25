import api from './api';

export const getLotes = () => api.get('/inventory/batches');
export const getLote = (id) => api.get(`/inventory/batches/${id}`);
export const getLoteErrors = (id) => api.get(`/inventory/batches/${id}/errors`);
export const getLoteItems = (id) => api.get(`/inventory/batches/${id}/items`);

export const uploadInventory = (file) => {
  const formData = new FormData();
  formData.append('file', file);
  return api.upload('/inventory/batches/upload', formData);
};

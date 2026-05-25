const BASE_URL = (import.meta.env.VITE_BFF_URL || 'http://localhost:8009') + '/api';

function getAuthHeader() {
  const token = localStorage.getItem('bf_access_token');
  return token ? { Authorization: `Bearer ${token}` } : {};
}

async function request(path, options = {}) {
  const res = await fetch(`${BASE_URL}${path}`, {
    ...options,
    headers: {
      Accept: 'application/json',
      ...getAuthHeader(),
      ...options.headers,
      ...(options.body && typeof options.body === 'string'
        ? { 'Content-Type': 'application/json' }
        : {}),
    },
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || `Error ${res.status}: ${res.statusText}`);
  }
  return res.json();
}

const api = {
  get: (path) => request(path),
  post: (path, body) =>
    request(path, { method: 'POST', body: JSON.stringify(body) }),
  put: (path, body) =>
    request(path, { method: 'PUT', body: JSON.stringify(body) }),
  upload: async (path, formData) => {
    const res = await fetch(`${BASE_URL}${path}`, {
      method: 'POST',
      body: formData,
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || `Error ${res.status}`);
    }
    return res.json();
  },
};

export { BASE_URL };
export default api;

import { create } from 'zustand';

const TOKEN_KEY = 'bf_access_token';
const REFRESH_KEY = 'bf_refresh_token';
const USER_KEY = 'bf_user';

function decodeJwtPayload(token) {
  try {
    const base64 = token.split('.')[1].replace(/-/g, '+').replace(/_/g, '/');
    return JSON.parse(atob(base64));
  } catch {
    return {};
  }
}

function loadStored() {
  try {
    const token = localStorage.getItem(TOKEN_KEY);
    const raw = localStorage.getItem(USER_KEY);
    const user = raw ? JSON.parse(raw) : null;
    return { token, user };
  } catch {
    return { token: null, user: null };
  }
}

const stored = loadStored();

export const useAuthStore = create((set, get) => ({
  token: stored.token,
  user: stored.user,

  login: (accessToken, refreshToken, user) => {
    localStorage.setItem(TOKEN_KEY, accessToken);
    localStorage.setItem(REFRESH_KEY, refreshToken);
    localStorage.setItem(USER_KEY, JSON.stringify(user));
    set({ token: accessToken, user });
  },

  logout: async () => {
    const { token } = get();
    if (token) {
      try {
        const bff = import.meta.env.VITE_BFF_URL || 'http://localhost:8009';
        await fetch(`${bff}/api/auth/logout`, {
          method: 'POST',
          headers: { Authorization: `Bearer ${token}` },
        });
      } catch { /* ignore */ }
    }
    localStorage.removeItem(TOKEN_KEY);
    localStorage.removeItem(REFRESH_KEY);
    localStorage.removeItem(USER_KEY);
    set({ token: null, user: null });
  },

  isAuthenticated: () => !!get().token,
}));

export { decodeJwtPayload, TOKEN_KEY };

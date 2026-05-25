import axios, { AxiosInstance, InternalAxiosRequestConfig } from "axios";

const BFF = import.meta.env.VITE_BFF_URL || "http://localhost:8009";

let isRefreshing = false;
let failedQueue: Array<{ resolve: (token: string) => void; reject: (err: unknown) => void }> = [];

function processQueue(error: unknown, token: string | null) {
  failedQueue.forEach(({ resolve, reject }) => {
    if (error) reject(error);
    else resolve(token!);
  });
  failedQueue = [];
}

function clearAuthAndRedirect() {
  localStorage.removeItem("bf_access_token");
  localStorage.removeItem("bf_refresh_token");
  localStorage.removeItem("bf_user");
  window.location.href = "/";
}

export const authAxios: AxiosInstance = axios.create();

authAxios.interceptors.request.use((config: InternalAxiosRequestConfig) => {
  const token = localStorage.getItem("bf_access_token");
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

authAxios.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config as InternalAxiosRequestConfig & { _retry?: boolean };

    if (error.response?.status !== 401 || originalRequest._retry) {
      return Promise.reject(error);
    }

    originalRequest._retry = true;

    if (isRefreshing) {
      return new Promise<string>((resolve, reject) => {
        failedQueue.push({ resolve, reject });
      }).then((token) => {
        originalRequest.headers.Authorization = `Bearer ${token}`;
        return authAxios(originalRequest);
      });
    }

    isRefreshing = true;

    const refreshToken = localStorage.getItem("bf_refresh_token");
    if (!refreshToken) {
      isRefreshing = false;
      clearAuthAndRedirect();
      return Promise.reject(error);
    }

    try {
      const res = await axios.post(`${BFF}/api/auth/refresh`, { refresh_token: refreshToken });
      const { access_token } = res.data as { access_token: string };
      localStorage.setItem("bf_access_token", access_token);
      processQueue(null, access_token);
      originalRequest.headers.Authorization = `Bearer ${access_token}`;
      return authAxios(originalRequest);
    } catch (refreshError) {
      processQueue(refreshError, null);
      clearAuthAndRedirect();
      return Promise.reject(refreshError);
    } finally {
      isRefreshing = false;
    }
  },
);

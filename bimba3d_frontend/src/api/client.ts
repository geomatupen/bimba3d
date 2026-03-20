import axios from "axios";

const hostname = typeof window !== 'undefined' ? window.location.hostname : '';
const port = typeof window !== 'undefined' ? window.location.port : '';
const protocol = typeof window !== 'undefined' ? window.location.protocol : 'http:';

const isViteDevPort = port === '5173' || port === '5174';

const baseURL = hostname === 'app.bimba3d.com'
  ? 'https://backend.bimba3d.com'
  : isViteDevPort
    ? `${protocol}//${hostname || 'localhost'}:8005`
    : `${protocol}//${hostname}${port ? `:${port}` : ''}`;

export const api = axios.create({
  baseURL,
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem("bimba3d:accessToken");
  if (token) {
    config.headers = config.headers ?? {};
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

let refreshPromise: Promise<string | null> | null = null;

api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config as any;
    if (!originalRequest || error.response?.status !== 401 || originalRequest._retry) {
      return Promise.reject(error);
    }

    const refreshToken = localStorage.getItem("bimba3d:refreshToken");
    if (!refreshToken) {
      return Promise.reject(error);
    }

    originalRequest._retry = true;

    if (!refreshPromise) {
      refreshPromise = api
        .post("/auth/refresh", { refresh_token: refreshToken })
        .then((res) => {
          const nextAccessToken = res.data?.access_token as string | undefined;
          const nextRefreshToken = res.data?.refresh_token as string | undefined;
          const nextUser = res.data?.user;
          if (!nextAccessToken || !nextRefreshToken || !nextUser) return null;
          localStorage.setItem("bimba3d:accessToken", nextAccessToken);
          localStorage.setItem("bimba3d:refreshToken", nextRefreshToken);
          localStorage.setItem("bimba3d:user", JSON.stringify({
            id: nextUser.id,
            name: nextUser.name,
            email: nextUser.email,
          }));
          return nextAccessToken;
        })
        .catch(() => {
          localStorage.removeItem("bimba3d:accessToken");
          localStorage.removeItem("bimba3d:refreshToken");
          localStorage.removeItem("bimba3d:user");
          return null;
        })
        .finally(() => {
          refreshPromise = null;
        });
    }

    const renewedToken = await refreshPromise;
    if (!renewedToken) {
      return Promise.reject(error);
    }

    originalRequest.headers = originalRequest.headers ?? {};
    originalRequest.headers.Authorization = `Bearer ${renewedToken}`;
    return api.request(originalRequest);
  }
);

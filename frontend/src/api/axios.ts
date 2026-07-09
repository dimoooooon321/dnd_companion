import axios from 'axios';
import { clearAuthSession, notifyAuthInvalidated, readAuthSession } from '../lib/authSession';

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL ?? 'http://localhost:8000',
});

api.interceptors.request.use((config) => {
  const token = readAuthSession()?.token;
  if (token) {
    if (!config.headers) {
      config.headers = { Authorization: `Bearer ${token}` } as never;
    } else {
      const headers = config.headers as unknown as {
        Authorization?: string;
        authorization?: string;
      };

      if (headers.Authorization == null && headers.authorization == null) {
        headers.Authorization = `Bearer ${token}`;
      }
    }
  }

  return config;
});

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (axios.isAxiosError(error) && error.response?.status === 401) {
      clearAuthSession();
      notifyAuthInvalidated();
    }

    return Promise.reject(error);
  }
);

export default api;

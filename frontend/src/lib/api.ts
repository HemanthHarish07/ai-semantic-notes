import axios from 'axios';
import { clearToken } from './token';

const API_URL = (import.meta as any).env?.VITE_API_URL || 'http://127.0.0.1:8000';

export const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Cache-Control': 'no-store, no-cache, must-revalidate, proxy-revalidate',
    'Pragma': 'no-cache',
    'Expires': '0',
  },
});

// Add request interceptor to ensure fresh data
api.interceptors.request.use((config) => {
  // Add cache-busting timestamp to GET requests
  if (config.method === 'get') {
    config.params = config.params || {};
    config.params._ts = Date.now();
  }
  return config;
});

// Add response interceptor to handle 401 Unauthorized errors automatically
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response && error.response.status === 401) {
      console.warn('[API] 401 Unauthorized/Session Expired detected. Clearing token and redirecting...');
      clearToken();
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// NOTE: Backend contract uses query-param `access_token` (not Authorization header).
// This is intentionally omitted to avoid accidental misuse.



/**
 * Sanyukt ID — API Client
 * Centralized fetch wrapper for all API calls
 */
const API_BASE = 'http://localhost:8000';

const api = {
  async request(method, path, body = null, requiresAuth = true) {
    const headers = { 'Content-Type': 'application/json' };
    if (requiresAuth) {
      const token = localStorage.getItem('sanyukt_token');
      if (token) headers['Authorization'] = `Bearer ${token}`;
    }
    const opts = { method, headers };
    if (body) opts.body = JSON.stringify(body);
    const resp = await fetch(API_BASE + path, opts);
    if (resp.status === 401) {
      auth.logout();
      return null;
    }
    const data = await resp.json().catch(() => ({ detail: resp.statusText }));
    if (!resp.ok) throw new Error(data.detail || 'Request failed');
    return data;
  },
  get: (path, auth = true) => api.request('GET', path, null, auth),
  post: (path, body, auth = true) => api.request('POST', path, body, auth),
  delete: (path, body, auth = true) => api.request('DELETE', path, body, auth),
};

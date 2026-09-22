/**
 * Sanyukt ID — API Client
 * Centralized fetch wrapper for all API calls
 */
// Automatically use relative URLs in production or same-origin local (e.g. Render, or localhost:8000),
// and fallback to http://localhost:8000 only when served from a separate static server/file protocol.
const API_BASE = (window.location.protocol === 'file:' || 
  ((window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') && 
   window.location.port !== '8000' && window.location.port !== ''))
  ? 'http://localhost:8000'
  : '';

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

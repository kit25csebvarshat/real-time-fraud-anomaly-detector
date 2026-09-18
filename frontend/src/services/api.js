const API_BASE = '/api';

async function request(endpoint, options = {}) {
  const token = localStorage.getItem('oauthguard_token');
  const headers = {
    'Content-Type': 'application/json',
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
    ...options.headers,
  };

  const response = await fetch(`${API_BASE}${endpoint}`, {
    ...options,
    headers,
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({ detail: 'Network request failed' }));
    throw new Error(errorData.detail || `Error ${response.status}: ${response.statusText}`);
  }

  return response.json();
}

export const api = {
  // Auth
  login: (email, password) =>
    request('/auth/login', {
      method: 'POST',
      body: JSON.stringify({ email, password }),
    }),
  getMe: () => request('/auth/me'),

  // Dashboard
  getDashboardStats: () => request('/dashboard/stats'),

  // Applications
  getApps: (status = '', search = '') => {
    const params = new URLSearchParams();
    if (status) params.append('status', status);
    if (search) params.append('search', search);
    const query = params.toString() ? `?${params.toString()}` : '';
    return request(`/apps${query}`);
  },

  getApp: (id) => request(`/apps/${id}`),
  createApp: (appData) =>
    request('/apps', {
      method: 'POST',
      body: JSON.stringify(appData),
    }),

  scanApp: (id) =>
    request(`/apps/${id}/scan`, {
      method: 'POST',
    }),

  getAppRisk: (id) => request(`/apps/${id}/risk`),
  getAppExplanation: (id) => request(`/apps/${id}/explanation`),

  // Admin Actions
  markTrusted: (id, reason = 'Administrator manual trust approval') =>
    request(`/apps/${id}/trust`, {
      method: 'POST',
      body: JSON.stringify({ reason }),
    }),

  markReview: (id, reason = 'Flagged for detailed security review') =>
    request(`/apps/${id}/review`, {
      method: 'POST',
      body: JSON.stringify({ reason }),
    }),

  revokeAccess: (id, reason = 'SIMULATED ACTION: Access revoked by security admin') =>
    request(`/apps/${id}/revoke`, {
      method: 'POST',
      body: JSON.stringify({ reason }),
    }),

  // What-If Simulator
  simulatePermissions: (id, permissions) =>
    request(`/apps/${id}/simulate`, {
      method: 'POST',
      body: JSON.stringify({ permissions }),
    }),

  // Audit Logs
  getAuditLogs: (action = '', search = '') => {
    const params = new URLSearchParams();
    if (action) params.append('action', action);
    if (search) params.append('search', search);
    const query = params.toString() ? `?${params.toString()}` : '';
    return request(`/audit-logs${query}`);
  },
};

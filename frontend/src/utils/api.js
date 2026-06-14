const API_BASE = '';

export function authHeaders(token) {
  return token ? { Authorization: `Bearer ${token}` } : {};
}

export async function apiFetch(path, token, options = {}) {
  const res = await fetch(`${API_BASE}${path}`, {
    ...options,
    headers: {
      ...authHeaders(token),
      ...(options.headers || {}),
    },
  });
  return res;
}

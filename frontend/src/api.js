const BASE = "/api";

async function request(path, options = {}) {
  const res = await fetch(`${BASE}${path}`, {
    headers: { "Content-Type": "application/json", ...options.headers },
    ...options,
  });
  if (res.status === 204) return null;
  const data = await res.json().catch(() => ({}));
  if (!res.ok) {
    throw new Error(data.error || `Error HTTP ${res.status}`);
  }
  return data;
}

export const api = {
  health: () => request("/health"),
  listDevices: () => request("/dispositivos"),
  getDevice: (id) => request(`/dispositivos/${encodeURIComponent(id)}`),
  searchDevice: (id) =>
    request(`/dispositivos/buscar?${new URLSearchParams({ id })}`),
  createDevice: (body) =>
    request("/dispositivos", { method: "POST", body: JSON.stringify(body) }),
  updateDevice: (id, body) =>
    request(`/dispositivos/${encodeURIComponent(id)}`, {
      method: "PUT",
      body: JSON.stringify(body),
    }),
  deleteDevice: (id) =>
    request(`/dispositivos/${encodeURIComponent(id)}`, { method: "DELETE" }),
  updateEstado: (id, estado) =>
    request(`/dispositivos/${encodeURIComponent(id)}/estado`, {
      method: "PATCH",
      body: JSON.stringify({ estado }),
    }),
  diagnostico: (id) =>
    request(`/dispositivos/${encodeURIComponent(id)}/diagnostico`, {
      method: "POST",
    }),
  diagnosticoTodos: () =>
    request("/diagnosticos/ejecutar-todos", { method: "POST" }),
  seed: () => request("/demo/semilla", { method: "POST" }),
};

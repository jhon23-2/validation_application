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
  createDevice: (body) => request("/dispositivos", { method: "POST", body: JSON.stringify(body) }),
  deleteDevice: (id) => request(`/dispositivos/${id}`, { method: "DELETE" }),
  patchEstado: (id, estado) =>
    request(`/dispositivos/${id}/estado`, {
      method: "PATCH",
      body: JSON.stringify({ estado }),
    }),
  diagnostico: (id) => request(`/dispositivos/${id}/diagnostico`, { method: "POST" }),
  diagnosticoTodos: () => request("/diagnosticos/ejecutar-todos", { method: "POST" }),
  seed: () => request("/demo/semilla", { method: "POST" }),
};

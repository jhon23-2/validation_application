import { useState } from "react";

const empty = {
  tipo: "router",
  nombre: "",
  ip: "",
  ubicacion: "",
  estado: "activo",
  tablas_enrutamiento: 4,
  ancho_banda_mbps: 1000,
  puertos: 24,
  vlan_count: 1,
};

export default function DeviceForm({ onSubmit, estados, compact = false }) {
  const [form, setForm] = useState(empty);
  const [saving, setSaving] = useState(false);

  const set = (key, value) => setForm((f) => ({ ...f, [key]: value }));

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSaving(true);
    const payload = {
      tipo: form.tipo,
      nombre: form.nombre,
      ip: form.ip,
      ubicacion: form.ubicacion,
      estado: form.estado,
    };
    if (form.tipo === "router") {
      payload.tablas_enrutamiento = Number(form.tablas_enrutamiento);
      payload.ancho_banda_mbps = Number(form.ancho_banda_mbps);
    } else {
      payload.puertos = Number(form.puertos);
      payload.vlan_count = Number(form.vlan_count);
    }
    try {
      await onSubmit(payload);
      setForm({ ...empty, tipo: form.tipo });
    } finally {
      setSaving(false);
    }
  };

  return (
    <form className={`form${compact ? " form-compact" : ""}`} onSubmit={handleSubmit}>
      <label>
        Tipo
        <select value={form.tipo} onChange={(e) => set("tipo", e.target.value)}>
          <option value="router">Router</option>
          <option value="switch">Switch</option>
        </select>
      </label>
      <label>
        Nombre
        <input
          required
          minLength={2}
          value={form.nombre}
          onChange={(e) => set("nombre", e.target.value)}
          placeholder="R-Core-Lab"
        />
      </label>
      <label>
        Dirección IP
        <input
          required
          value={form.ip}
          onChange={(e) => set("ip", e.target.value)}
          placeholder="192.168.1.1"
        />
      </label>
      <label>
        Ubicación
        <input
          required
          value={form.ubicacion}
          onChange={(e) => set("ubicacion", e.target.value)}
          placeholder="Edificio A — Rack 2"
        />
      </label>
      <label>
        Estado
        <select value={form.estado} onChange={(e) => set("estado", e.target.value)}>
          {estados.map((s) => (
            <option key={s} value={s}>
              {s}
            </option>
          ))}
        </select>
      </label>

      {form.tipo === "router" ? (
        <>
          <label>
            Tablas de enrutamiento
            <input
              type="number"
              min={1}
              max={256}
              value={form.tablas_enrutamiento}
              onChange={(e) => set("tablas_enrutamiento", e.target.value)}
            />
          </label>
          <label>
            Ancho de banda (Mbps)
            <input
              type="number"
              min={1}
              step="0.1"
              value={form.ancho_banda_mbps}
              onChange={(e) => set("ancho_banda_mbps", e.target.value)}
            />
          </label>
        </>
      ) : (
        <>
          <label>
            Puertos
            <input
              type="number"
              min={4}
              max={128}
              value={form.puertos}
              onChange={(e) => set("puertos", e.target.value)}
            />
          </label>
          <label>
            VLANs
            <input
              type="number"
              min={1}
              value={form.vlan_count}
              onChange={(e) => set("vlan_count", e.target.value)}
            />
          </label>
        </>
      )}

      <button type="submit" className="btn primary" disabled={saving}>
        {saving ? "Guardando…" : "Registrar"}
      </button>
    </form>
  );
}

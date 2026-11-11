import { useCallback, useEffect, useState } from "react";
import { api } from "./api";
import DeviceDetail from "./components/DeviceDetail";
import DeviceForm from "./components/DeviceForm";
import DeviceList from "./components/DeviceList";
import DeviceSearch from "./components/DeviceSearch";
import DiagnosticsPanel from "./components/DiagnosticsPanel";

const ESTADOS = ["activo", "inactivo", "mantenimiento", "falla"];

export default function App() {
  const [devices, setDevices] = useState([]);
  const [selected, setSelected] = useState(null);
  const [searchId, setSearchId] = useState("");
  const [searchBusy, setSearchBusy] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const [diagnostics, setDiagnostics] = useState([]);
  const [apiOk, setApiOk] = useState(false);
  const [showCreate, setShowCreate] = useState(false);

  const refresh = useCallback(async () => {
    setError("");
    try {
      const [health, list] = await Promise.all([api.health(), api.listDevices()]);
      setApiOk(health?.status === "ok");
      setDevices(list);
      setSelected((prev) => {
        if (!prev) return null;
        return list.find((d) => d.id === prev.id) ?? null;
      });
    } catch (e) {
      setError(e.message || "No se pudo conectar con la API.");
      setApiOk(false);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    refresh();
  }, [refresh]);

  const flash = (msg) => {
    setSuccess(msg);
    window.setTimeout(() => setSuccess(""), 2800);
  };

  const onCreate = async (payload) => {
    setError("");
    try {
      const created = await api.createDevice(payload);
      await refresh();
      setSelected(created);
      setShowCreate(false);
      flash("Dispositivo creado.");
    } catch (e) {
      setError(e.message);
      throw e;
    }
  };

  const onSearch = async () => {
    setError("");
    setSearchBusy(true);
    try {
      const found = await api.searchDevice(searchId.trim());
      setSelected(found);
      flash("Equipo encontrado.");
    } catch (e) {
      setError(e.message);
      setSelected(null);
    } finally {
      setSearchBusy(false);
    }
  };

  const onUpdateEstado = async (id, estado) => {
    setError("");
    try {
      const updated = await api.updateEstado(id, estado);
      setSelected(updated);
      await refresh();
      flash("Estado actualizado.");
    } catch (e) {
      setError(e.message);
    }
  };

  const onUpdate = async (id, body) => {
    setError("");
    try {
      const updated = await api.updateDevice(id, body);
      setSelected(updated);
      await refresh();
      flash("Datos guardados.");
    } catch (e) {
      setError(e.message);
    }
  };

  const onDelete = async (id) => {
    setError("");
    try {
      await api.deleteDevice(id);
      setSelected(null);
      await refresh();
      flash("Dispositivo eliminado.");
    } catch (e) {
      setError(e.message);
    }
  };

  const onDiagnostico = async (id) => {
    setError("");
    try {
      const result = await api.diagnostico(id);
      setDiagnostics([result]);
    } catch (e) {
      setError(e.message);
    }
  };

  const onSeed = async () => {
    setError("");
    try {
      await api.seed();
      await refresh();
      flash("Datos demo listos.");
    } catch (e) {
      setError(e.message);
    }
  };

  return (
    <div className="app app-min">
      <header className="topbar">
        <div>
          <h1>Lab Redes</h1>
          <p className="muted">CRUD · buscar por ID · estado · eliminar</p>
        </div>
        <VersionPills apiOk={apiOk} count={devices.length} />
      </header>

      {error && (
        <div className="alert" role="alert">
          {error}
        </div>
      )}
      {success && (
        <div className="toast" role="status">
          {success}
        </div>
      )}

      <main className="crud-layout">
        <section className="panel">
          <DeviceSearch
            value={searchId}
            onChange={setSearchId}
            onSearch={onSearch}
            busy={searchBusy}
          />

          <div className="panel-toolbar">
            <button
              type="button"
              className="btn ghost"
              onClick={() => setShowCreate((v) => !v)}
            >
              {showCreate ? "Ocultar formulario" : "+ Nuevo dispositivo"}
            </button>
            <button type="button" className="btn ghost" onClick={onSeed}>
              Demo
            </button>
          </div>

          {showCreate && (
            <DeviceForm onSubmit={onCreate} estados={ESTADOS} compact />
          )}
        </section>

        <section className="panel">
          <h2 className="section-title">Inventario</h2>
          {loading ? (
            <p className="muted">Cargando…</p>
          ) : (
            <DeviceList
              devices={devices}
              selectedId={selected?.id}
              onSelect={setSelected}
            />
          )}
        </section>

        <section className="panel">
          <h2 className="section-title">Detalle</h2>
          <DeviceDetail
            device={selected}
            estados={ESTADOS}
            onUpdateEstado={onUpdateEstado}
            onUpdate={onUpdate}
            onDelete={onDelete}
            onDiagnostico={onDiagnostico}
            onClear={() => setSelected(null)}
          />
        </section>

        {diagnostics.length > 0 && (
          <section className="panel panel-span">
            <h2 className="section-title">Diagnóstico</h2>
            <DiagnosticsPanel items={diagnostics} />
          </section>
        )}
      </main>
    </div>
  );
}

function VersionPills({ apiOk, count }) {
  return (
    <div className="pills">
      <span className={`pill ${apiOk ? "pill-ok" : "pill-warn"}`}>
        {apiOk ? "En línea" : "Sin API"}
      </span>
      <span className="pill">{count}</span>
    </div>
  );
}

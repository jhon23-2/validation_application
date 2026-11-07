import { useCallback, useEffect, useState } from "react";
import { api } from "./api";
import DeviceForm from "./components/DeviceForm";
import DeviceList from "./components/DeviceList";
import DiagnosticsPanel from "./components/DiagnosticsPanel";

const ESTADOS = ["activo", "inactivo", "mantenimiento", "falla"];

export default function App() {
  const [devices, setDevices] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [diagnostics, setDiagnostics] = useState([]);
  const [apiOk, setApiOk] = useState(false);

  const refresh = useCallback(async () => {
    setError("");
    try {
      const [health, list] = await Promise.all([api.health(), api.listDevices()]);
      setApiOk(health?.status === "ok");
      setDevices(list);
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

  const onCreate = async (payload) => {
    setError("");
    try {
      await api.createDevice(payload);
      await refresh();
    } catch (e) {
      setError(e.message);
      throw e;
    }
  };

  const onDelete = async (id) => {
    setError("");
    try {
      await api.deleteDevice(id);
      await refresh();
    } catch (e) {
      setError(e.message);
    }
  };

  const onEstado = async (id, estado) => {
    setError("");
    try {
      await api.patchEstado(id, estado);
      await refresh();
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

  const onDiagnosticoTodos = async () => {
    setError("");
    try {
      const results = await api.diagnosticoTodos();
      setDiagnostics(results);
    } catch (e) {
      setError(e.message);
    }
  };

  const onSeed = async () => {
    setError("");
    try {
      await api.seed();
      await refresh();
    } catch (e) {
      setError(e.message);
    }
  };

  return (
    <div className="app">
      <header className="hero">
        <div className="hero-text">
          <p className="eyebrow">POO · Redes · Campus</p>
          <h1>Laboratorio de redes</h1>
          <p className="subtitle">
            Inventario de routers y switches con diagnóstico polimórfico (
            <code>ejecutar_diagnostico</code>).
          </p>
        </div>
        <div className="hero-meta">
          <span className={`pill ${apiOk ? "pill-ok" : "pill-warn"}`}>
            API {apiOk ? "conectada" : "desconectada"}
          </span>
          <span className="pill">{devices.length} dispositivo(s)</span>
        </div>
      </header>

      {error && (
        <div className="alert" role="alert">
          {error}
        </div>
      )}

      <main className="layout">
        <section className="panel">
          <div className="panel-head">
            <h2>Nuevo dispositivo</h2>
            <button type="button" className="btn ghost" onClick={onSeed}>
              Cargar datos demo
            </button>
          </div>
          <DeviceForm onSubmit={onCreate} estados={ESTADOS} />
        </section>

        <section className="panel panel-wide">
          <div className="panel-head">
            <h2>Inventario</h2>
            <button
              type="button"
              className="btn primary"
              onClick={onDiagnosticoTodos}
              disabled={!devices.length}
            >
              Diagnóstico global
            </button>
          </div>
          {loading ? (
            <p className="muted">Cargando…</p>
          ) : (
            <DeviceList
              devices={devices}
              estados={ESTADOS}
              onDelete={onDelete}
              onEstado={onEstado}
              onDiagnostico={onDiagnostico}
            />
          )}
        </section>

        <section className="panel panel-wide">
          <h2>Resultados de diagnóstico</h2>
          <DiagnosticsPanel items={diagnostics} />
        </section>
      </main>

      <footer className="footer">
        Backend: Flask · Modelos: <code>DispositivoRed</code>, <code>Router</code>,{" "}
        <code>Switch</code>
      </footer>
    </div>
  );
}

import { useEffect, useState } from "react";

export default function DeviceDetail({
  device,
  estados,
  onUpdateEstado,
  onUpdate,
  onDelete,
  onDiagnostico,
  onClear,
}) {
  const [estado, setEstado] = useState(device?.estado ?? "activo");
  const [edit, setEdit] = useState({
    nombre: "",
    ip: "",
    ubicacion: "",
  });

  useEffect(() => {
    if (!device) return;
    setEstado(device.estado);
    setEdit({
      nombre: device.nombre,
      ip: device.ip,
      ubicacion: device.ubicacion,
    });
  }, [device]);

  if (!device) {
    return (
      <div className="detail empty">
        <p className="muted">
          Selecciona un equipo de la lista o búscalo por ID para ver detalle y
          operaciones CRUD.
        </p>
      </div>
    );
  }

  const shortId = `${device.id.slice(0, 8)}…`;

  const handleDelete = () => {
    if (
      window.confirm(
        `¿Eliminar "${device.nombre}"?\nEsta acción no se puede deshacer.`
      )
    ) {
      onDelete(device.id);
    }
  };

  return (
    <article className="detail">
      <header className="detail-head">
        <div>
          <span className={`tipo tipo-${device.tipo}`}>{device.tipo}</span>
          <h3>{device.nombre}</h3>
        </div>
        <button type="button" className="btn ghost sm" onClick={onClear}>
          Cerrar
        </button>
      </header>

      <dl className="detail-meta">
        <div>
          <dt>ID</dt>
          <dd>
            <code title={device.id}>{shortId}</code>
            <button
              type="button"
              className="btn link"
              onClick={() => navigator.clipboard?.writeText(device.id)}
            >
              Copiar
            </button>
          </dd>
        </div>
        <div>
          <dt>IP</dt>
          <dd>
            <code>{device.ip}</code>
          </dd>
        </div>
        <div>
          <dt>Ubicación</dt>
          <dd>{device.ubicacion}</dd>
        </div>
      </dl>

      <div className="detail-block">
        <h4>Actualizar estado</h4>
        <div className="row">
          <select
            value={estado}
            onChange={(e) => setEstado(e.target.value)}
            aria-label="Estado del dispositivo"
          >
            {estados.map((s) => (
              <option key={s} value={s}>
                {s}
              </option>
            ))}
          </select>
          <button
            type="button"
            className="btn primary"
            onClick={() => onUpdateEstado(device.id, estado)}
          >
            Guardar estado
          </button>
        </div>
      </div>

      <div className="detail-block">
        <h4>Editar datos</h4>
        <form
          className="mini-form"
          onSubmit={(e) => {
            e.preventDefault();
            onUpdate(device.id, { ...edit, estado });
          }}
        >
          <input
            value={edit.nombre}
            onChange={(e) => setEdit((f) => ({ ...f, nombre: e.target.value }))}
            placeholder="Nombre"
            required
            minLength={2}
          />
          <input
            value={edit.ip}
            onChange={(e) => setEdit((f) => ({ ...f, ip: e.target.value }))}
            placeholder="IP"
            required
          />
          <input
            value={edit.ubicacion}
            onChange={(e) =>
              setEdit((f) => ({ ...f, ubicacion: e.target.value }))
            }
            placeholder="Ubicación"
            required
          />
          <button type="submit" className="btn">
            Guardar cambios
          </button>
        </form>
      </div>

      <div className="detail-actions">
        <button type="button" className="btn" onClick={() => onDiagnostico(device.id)}>
          Diagnóstico
        </button>
        <button type="button" className="btn danger" onClick={handleDelete}>
          Eliminar
        </button>
      </div>
    </article>
  );
}

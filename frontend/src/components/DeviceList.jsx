function estadoClass(estado) {
  return `badge badge-${estado}`;
}

export default function DeviceList({ devices, estados, onDelete, onEstado, onDiagnostico }) {
  if (!devices.length) {
    return <p className="muted">No hay equipos. Registra uno o carga la demo.</p>;
  }

  return (
    <div className="table-wrap">
      <table className="table">
        <thead>
          <tr>
            <th>Equipo</th>
            <th>IP</th>
            <th>Ubicación</th>
            <th>Estado</th>
            <th>Detalles</th>
            <th aria-label="Acciones" />
          </tr>
        </thead>
        <tbody>
          {devices.map((d) => (
            <tr key={d.id}>
              <td>
                <span className={`tipo tipo-${d.tipo}`}>{d.tipo}</span>
                <strong>{d.nombre}</strong>
              </td>
              <td>
                <code>{d.ip}</code>
              </td>
              <td>{d.ubicacion}</td>
              <td>
                <select
                  className={estadoClass(d.estado)}
                  value={d.estado}
                  onChange={(e) => onEstado(d.id, e.target.value)}
                  aria-label={`Estado de ${d.nombre}`}
                >
                  {estados.map((s) => (
                    <option key={s} value={s}>
                      {s}
                    </option>
                  ))}
                </select>
              </td>
              <td className="detalles">
                {d.tipo === "router" ? (
                  <>
                    {d.detalles.tablas_enrutamiento} rutas · {d.detalles.ancho_banda_mbps} Mbps
                  </>
                ) : (
                  <>
                    {d.detalles.puertos} puertos · {d.detalles.vlan_count} VLANs
                  </>
                )}
              </td>
              <td className="actions">
                <button type="button" className="btn sm" onClick={() => onDiagnostico(d.id)}>
                  Diagnóstico
                </button>
                <button
                  type="button"
                  className="btn sm danger"
                  onClick={() => onDelete(d.id)}
                >
                  Eliminar
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

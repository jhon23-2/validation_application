export default function DeviceList({ devices, selectedId, onSelect }) {
  if (!devices.length) {
    return <p className="muted">No hay equipos. Crea uno o carga la demo.</p>;
  }

  return (
    <ul className="device-list">
      {devices.map((d) => (
        <li key={d.id}>
          <button
            type="button"
            className={`device-row${selectedId === d.id ? " selected" : ""}`}
            onClick={() => onSelect(d)}
          >
            <span className={`tipo tipo-${d.tipo}`}>{d.tipo}</span>
            <span className="device-row-name">{d.nombre}</span>
            <code className="device-row-ip">{d.ip}</code>
            <span className={`estado-dot estado-${d.estado}`}>{d.estado}</span>
          </button>
        </li>
      ))}
    </ul>
  );
}

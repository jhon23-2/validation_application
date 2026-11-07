export default function DiagnosticsPanel({ items }) {
  if (!items?.length) {
    return (
      <p className="muted">
        Ejecuta un diagnóstico por equipo o el barrido global para ver polimorfismo en acción.
      </p>
    );
  }

  return (
    <ul className="diag-list">
      {items.map((item, idx) => (
        <li key={`${item.dispositivo}-${idx}`} className="diag-card">
          <div className="diag-head">
            <span className={`tipo tipo-${item.tipo}`}>{item.tipo}</span>
            <strong>{item.dispositivo}</strong>
            <span className="muted">· {item.prueba}</span>
          </div>
          <p>{item.mensaje}</p>
          <pre>{JSON.stringify(item, null, 2)}</pre>
        </li>
      ))}
    </ul>
  );
}

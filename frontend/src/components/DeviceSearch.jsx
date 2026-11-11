export default function DeviceSearch({ value, onChange, onSearch, busy }) {
  return (
    <form
      className="search-bar"
      onSubmit={(e) => {
        e.preventDefault();
        onSearch();
      }}
    >
      <label className="sr-only" htmlFor="buscar-id">
        Buscar por ID
      </label>
      <input
        id="buscar-id"
        type="search"
        placeholder="Buscar por ID (mín. 4 caracteres)"
        value={value}
        onChange={(e) => onChange(e.target.value)}
        autoComplete="off"
      />
      <button type="submit" className="btn primary" disabled={busy}>
        {busy ? "…" : "Buscar"}
      </button>
    </form>
  );
}

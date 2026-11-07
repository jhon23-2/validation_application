# Laboratorio de redes — POO + Flask + React

Aplicación para la **Actividad 2 (POO en Python)** aplicada a la gestión de equipos de un laboratorio de redes: routers y switches con encapsulamiento, herencia, polimorfismo y excepciones personalizadas.

## Estructura del backend (requisitos académicos)

| Archivo | Responsabilidad |
|---------|-----------------|
| `backend/models.py` | Clase base `DispositivoRed`, subclases `Router` y `Switch`, polimorfismo en `ejecutar_diagnostico()` |
| `backend/excepciones_personalizadas.py` | `ExcepcionConfiguracionInvalida`, etc. |
| `backend/main.py` | Menú de consola, pruebas POO (`try/except/else/finally`) |
| `backend/app.py` | API REST Flask para el frontend React |
| `backend/repositorio.py` | Persistencia JSON (`backend/data/inventario.json`) |

## Requisitos

- Python 3.10+
- Node.js 18+

## Ejecución

### 1. Backend (API)

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python app.py
```

La API queda en `http://127.0.0.1:5000`.

### 2. Menú de consola y demo POO (entrega académica)

```powershell
cd backend
python main.py              # menú interactivo + pruebas al iniciar
python main.py --demo-poo   # solo bloque de pruebas
```

### 3. Frontend React

```powershell
cd frontend
npm install
npm run dev
```

Abre `http://localhost:5173`. Vite redirige `/api` al backend en el puerto 5000.

## Endpoints principales

- `GET /api/dispositivos` — listar inventario
- `POST /api/dispositivos` — crear router o switch (campo `tipo`)
- `POST /api/dispositivos/<id>/diagnostico` — diagnóstico polimórfico
- `POST /api/diagnosticos/ejecutar-todos` — diagnóstico de todos los equipos
- `POST /api/demo/semilla` — datos de ejemplo

## Conceptos POO implementados

1. **Encapsulamiento**: atributos privados (`__ip`, `__estado`, …) y validación con `@property` / `@setter`.
2. **Herencia**: `Router` y `Switch` extienden `DispositivoRed`.
3. **Polimorfismo**: mismo método `ejecutar_diagnostico()` con comportamiento distinto por tipo.
4. **Excepciones**: `ExcepcionConfiguracionInvalida` y bloques `try/except/else/finally` en `main.py` y `app.py`.

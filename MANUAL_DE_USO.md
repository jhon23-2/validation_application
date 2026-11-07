# Manual de uso — Laboratorio de redes

Este documento describe **todo lo que puedes hacer** en la aplicación, sin entrar en detalles de arquitectura ni instalación. Para compilar y ejecutar el proyecto, consulta el [README.md](README.md) principal.

---

## ¿Qué es esta aplicación?

Es un **inventario de equipos de red** de un laboratorio campus. Puedes registrar y administrar:

- **Routers** (enrutamiento, tablas de ruta, ancho de banda en Mbps).
- **Switches** (puertos Ethernet, VLANs).

Cada equipo tiene nombre, dirección **IPv4**, ubicación física y **estado operativo**. El sistema puede ejecutar **diagnósticos simulados** que cambian según el tipo de dispositivo (polimorfismo en POO).

Puedes usarla de **dos formas**:

1. **Interfaz web** (React) — la forma más cómoda para el día a día.
2. **Consola** (`main.py`) — menú por teclado y demostraciones para la actividad académica.

Los datos se **guardan en disco** (`backend/data/inventario.json`) y se comparten entre la web y la consola si usan el mismo backend.

---

## Formas de entrar al programa

| Cómo iniciar | Qué obtienes |
|--------------|--------------|
| Navegador en `http://localhost:5173` | Interfaz visual completa (requiere API Flask activa). |
| `python main.py` o `py -3 main.py` | Menú de consola + pruebas POO al inicio. |
| `python main.py --demo-poo` | Solo el bloque de demostración de objetos (sin menú). |
| `python main.py --serve` | API Flask desde el mismo punto de entrada (alternativa a `app.py`). |
| `python app.py` | Solo la API REST (para la web o herramientas externas). |

---

## Aplicación web (React)

Al abrir la página verás tres zonas: **nuevo dispositivo**, **inventario** y **resultados de diagnóstico**. En la cabecera aparecen el estado de la API y la cantidad de equipos.

### Comprobar que todo funciona

- Si la etiqueta dice **«API conectada»**, el frontend está hablando con Flask.
- Si dice **«API desconectada»**, debes levantar el backend (`app.py`) y recargar la página.
- El contador **«N dispositivo(s)»** se actualiza al cargar, crear o eliminar equipos.

### Cargar datos de demostración

**Botón:** *Cargar datos demo*

**Qué hace:**

- Si el inventario está **vacío**, crea automáticamente 3 equipos de ejemplo:
  - Router **R-Core-Lab** (10.0.0.1)
  - Switch **SW-Planta-2** (10.0.2.10)
  - Router **R-Borde** (192.168.100.1, en estado *mantenimiento*)
- Si **ya hay** dispositivos, no borra nada; solo informa que ya existen registros.

**Para qué sirve:** probar diagnósticos y la tabla sin rellenar el formulario manualmente.

### Registrar un equipo nuevo

**Sección:** *Nuevo dispositivo* → formulario → *Registrar*

**Qué puedes hacer:**

1. Elegir **tipo**: Router o Switch (el formulario cambia los campos).
2. Completar datos comunes:
   - **Nombre** (mínimo 2 caracteres)
   - **Dirección IP** (formato IPv4 válido, p. ej. `192.168.1.10`)
   - **Ubicación** (texto obligatorio)
   - **Estado**: `activo`, `inactivo`, `mantenimiento` o `falla`
3. Si es **Router**, además:
   - **Tablas de enrutamiento** (entero entre 1 y 256)
   - **Ancho de banda (Mbps)** (número mayor que 0)
4. Si es **Switch**, además:
   - **Puertos** (entre 4 y 128)
   - **VLANs** (entre 1 y el número de puertos)
5. Pulsar **Registrar**.

**Qué pasa después:**

- El equipo aparece en el inventario.
- Se guarda en `inventario.json`.
- Si algo no cumple las reglas, verás un mensaje de error en la franja roja superior (viene del servidor).

### Ver el inventario

**Sección:** *Inventario* (tabla)

**Qué puedes ver por cada fila:**

| Columna | Contenido |
|---------|-----------|
| Equipo | Tipo (router/switch) y nombre |
| IP | Dirección configurada |
| Ubicación | Lugar en el campus |
| Estado | Selector desplegable |
| Detalles | Routers: rutas y Mbps · Switches: puertos y VLANs |

La lista se ordena por nombre.

### Cambiar el estado de un equipo

**Dónde:** columna *Estado* en la tabla (desplegable)

**Estados posibles:**

| Estado | Efecto en la lógica |
|--------|---------------------|
| `activo` | Diagnóstico y capacidad «normales» |
| `inactivo` | Capacidad reducida o nula en simulaciones |
| `mantenimiento` | Routers: ancho de banda efectivo al 50 % |
| `falla` | Diagnóstico de router puede marcar salud *crítica* |

Al cambiar el estado, se guarda al instante en el servidor.

### Diagnóstico de un solo equipo

**Botón:** *Diagnóstico* en la fila del equipo

**Qué hace:**

- Llama a `ejecutar_diagnostico()` solo para ese dispositivo.
- Muestra el resultado en *Resultados de diagnóstico* (mensaje legible + JSON completo).

**Qué verás según el tipo:**

| Tipo | Prueba simulada | Datos típicos en el JSON |
|------|-----------------|---------------------------|
| Router | `traceroute_simulado` | saltos verificados, Mbps efectivos, `salud_enlace`, mensaje |
| Switch | `tabla_mac_simulada` | puertos activos, VLANs, capacidad agregada en Gbps, mensaje |

### Diagnóstico de todo el inventario

**Botón:** *Diagnóstico global* (arriba de la tabla)

**Qué hace:**

- Ejecuta diagnóstico en **todos** los equipos, uno tras otro.
- Muestra **varias tarjetas** en *Resultados de diagnóstico*, una por dispositivo.
- Sirve para comparar cómo un router y un switch responden al mismo tipo de operación (polimorfismo).

**Nota:** el botón se desactiva si no hay dispositivos en el inventario.

### Eliminar un equipo

**Botón:** *Eliminar* en la fila

**Qué hace:**

- Quita el dispositivo del inventario y actualiza el archivo JSON.
- La acción es **inmediata** (no hay diálogo de confirmación en la UI).

### Mensajes de error en la web

Si aparece la alerta roja superior, suele deberse a:

- API apagada o URL incorrecta.
- IP inválida, nombre muy corto, VLANs mayores que puertos, etc.
- Intentar operar sobre un ID que ya no existe (poco habitual en la UI).

El texto del error describe el problema en español.

---

## Consola (`main.py`)

Al ejecutar `main.py` sin argumentos, primero corre un **resumen automático de pruebas POO** (creación de objetos, excepciones, polimorfismo) y luego entra al **menú principal**.

### Menú principal — opciones

| Opción | Acción |
|--------|--------|
| **1** | **Listar dispositivos** — muestra ID (primeros 8 caracteres), tipo, nombre, IP y estado. |
| **2** | **Registrar router** — pide nombre, IP, ubicación, tablas de enrutamiento y ancho de banda. |
| **3** | **Registrar switch** — pide nombre, IP, ubicación, puertos y VLANs. |
| **4** | **Diagnóstico de un dispositivo** — pides el ID (o prefijo) y ves el diccionario de diagnóstico en consola. |
| **5** | **Diagnóstico de todos** — recorre el inventario y muestra cada diagnóstico (polimorfismo). |
| **6** | **Cambiar estado** — eliges equipo por ID y escribes el nuevo estado. |
| **7** | **Eliminar dispositivo** — borra por ID y guarda. |
| **8** | **Ejecutar pruebas POO** — repite el bloque de demostración académica. |
| **0** | **Salir y guardar** — persiste el inventario y cierra el programa. |

**Consejo:** en las opciones 4, 6 y 7 usa el prefijo de ID que viste en el listado (opción 1).

### Modo solo demostración (`--demo-poo`)

**Comando:** `python main.py --demo-poo`

**Qué puedes ver (sin interactuar):**

- Creación correcta de un router y un switch de prueba.
- Captura de **ExcepcionConfiguracionInvalida** (IP incorrecta).
- Captura de **IndexError** (acceso a lista fuera de rango).
- Salida de **ejecutar_diagnostico()** para cada tipo.

Ideal para mostrar el cumplimiento del enunciado POO al profesor.

---

## API REST (uso avanzado)

Si la aplicación web o Postman llaman al backend, estas son las operaciones disponibles. La web ya usa la mayoría.

| Acción | Método y ruta |
|--------|----------------|
| Comprobar servicio | `GET /api/health` |
| Listar inventario | `GET /api/dispositivos` |
| Ver un equipo | `GET /api/dispositivos/<id>` |
| Crear equipo | `POST /api/dispositivos` (JSON con `tipo`) |
| Cambiar estado | `PATCH /api/dispositivos/<id>/estado` |
| Eliminar | `DELETE /api/dispositivos/<id>` |
| Diagnóstico uno | `POST /api/dispositivos/<id>/diagnostico` |
| Diagnóstico todos | `POST /api/diagnosticos/ejecutar-todos` |
| Cargar demo | `POST /api/demo/semilla` |

Puedes integrar otras herramientas (scripts, Postman, otro frontend) con estos mismos endpoints.

---

## Reglas y límites (qué debes respetar al usar la app)

### Campos comunes (router y switch)

| Campo | Regla |
|-------|--------|
| Nombre | Mínimo 2 caracteres (sin contar espacios al inicio/final). |
| IP | Solo **IPv4** válida (cuatro octetos 0–255). |
| Ubicación | No puede quedar vacía. |
| Estado | Solo: `activo`, `inactivo`, `mantenimiento`, `falla`. |

### Solo routers

| Campo | Regla |
|-------|--------|
| Tablas de enrutamiento | Entero de **1** a **256**. |
| Ancho de banda (Mbps) | Número **mayor que 0**. |

### Solo switches

| Campo | Regla |
|-------|--------|
| Puertos | Entero de **4** a **128**. |
| VLANs | Entero de **1** hasta **número de puertos** (inclusive). |

### Tipos de equipo

Solo se aceptan `router` y `switch`. Cualquier otro valor en API o lógica interna es rechazado.

---

## Persistencia: qué se guarda y cuándo

| Evento | ¿Se guarda en disco? |
|--------|----------------------|
| Crear equipo (web o consola) | Sí |
| Cambiar estado | Sí |
| Eliminar equipo | Sí |
| Cargar datos demo | Sí (si inserta equipos) |
| Solo ejecutar diagnóstico | No modifica el inventario (solo lectura en memoria) |
| Salir del menú consola (opción 0) | Sí (guardado explícito al salir) |
| Pruebas `--demo-poo` | No afectan tu `inventario.json` (objetos en memoria temporal) |

Al reiniciar Flask, se **vuelve a cargar** el JSON; lo que veas en la web es el inventario persistido.

---

## Resumen: lista rápida de capacidades

```text
✔ Inventariar routers y switches del laboratorio
✔ Alta manual (web o consola)
✔ Carga rápida de 3 equipos demo
✔ Listar y consultar detalle (API)
✔ Cambiar estado operativo
✔ Eliminar equipos
✔ Diagnóstico individual (polimórfico)
✔ Diagnóstico masivo de todo el inventario
✔ Validación de datos con mensajes de error claros
✔ Persistencia en archivo JSON
✔ Demostración académica POO en consola
✔ Exponer las mismas funciones vía API REST
```

---

## Qué no hace esta aplicación (expectativas)

Para evitar confusiones:

- **No** se conecta a equipos reales por SSH, SNMP ni ping; los diagnósticos son **simulados** en código.
- **No** dibuja topologías de red en un canvas (solo inventario tabular).
- **No** tiene login de usuarios; es un proyecto de laboratorio/educación.
- **No** sincroniza con nube; todo es local en tu máquina.

---

## Flujo sugerido para probar todo en 5 minutos

1. Arranca API y web (ver [README.md](README.md)).
2. Pulsa **Cargar datos demo**.
3. Pulsa **Diagnóstico global** y revisa la diferencia router/switch en el panel inferior.
4. Cambia **R-Borde** a `falla` y vuelve a diagnosticarlo solo.
5. Registra un switch nuevo con datos válidos.
6. Elimínalo con **Eliminar**.
7. (Opcional) Abre consola con `main.py`, opción **1** y confirma que ves los mismos datos guardados.

Con eso habrás usado todas las funciones principales de la aplicación.

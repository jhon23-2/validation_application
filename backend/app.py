"""API REST Flask — laboratorio de redes (POO)."""

from __future__ import annotations

import os

from flask import Flask, jsonify, request
from flask_cors import CORS

from excepciones_personalizadas import (
    ExcepcionConfiguracionInvalida,
    ExcepcionDispositivoNoEncontrado,
)
from models import RegistroLaboratorio
from repositorio import RepositorioInventario

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": os.getenv("CORS_ORIGIN", "*")}})

_repo = RepositorioInventario()
_registro = _repo.cargar_registro()


def _persistir() -> None:
    _repo.guardar_registro(_registro)


@app.errorhandler(ExcepcionConfiguracionInvalida)
def _config_invalida(err: ExcepcionConfiguracionInvalida):
    return jsonify({"error": str(err), "campo": err.campo}), 400


@app.errorhandler(ExcepcionDispositivoNoEncontrado)
def _no_encontrado(err: ExcepcionDispositivoNoEncontrado):
    return jsonify({"error": str(err)}), 404


@app.get("/api/health")
def health():
    return jsonify({"status": "ok", "dispositivos": len(_registro.listar())})


@app.get("/api/dispositivos")
def listar_dispositivos():
    return jsonify([d.to_dict() for d in _registro.listar()])


@app.post("/api/dispositivos")
def crear_dispositivo():
    payload = request.get_json(silent=True) or {}
    try:
        dispositivo = RegistroLaboratorio.crear_desde_payload(payload)
    except ExcepcionConfiguracionInvalida:
        raise
    except (TypeError, ValueError) as err:
        raise ExcepcionConfiguracionInvalida(
            "Cuerpo JSON con tipos de datos incorrectos.", "body"
        ) from err
    else:
        _registro.agregar(dispositivo)
        _persistir()
        return jsonify(dispositivo.to_dict()), 201
    finally:
        pass


@app.get("/api/dispositivos/<dispositivo_id>")
def obtener_dispositivo(dispositivo_id: str):
    dispositivo = _registro.obtener(dispositivo_id)
    if not dispositivo:
        raise ExcepcionDispositivoNoEncontrado(dispositivo_id)
    return jsonify(dispositivo.to_dict())


@app.delete("/api/dispositivos/<dispositivo_id>")
def eliminar_dispositivo(dispositivo_id: str):
    if not _registro.eliminar(dispositivo_id):
        raise ExcepcionDispositivoNoEncontrado(dispositivo_id)
    _persistir()
    return "", 204


@app.patch("/api/dispositivos/<dispositivo_id>/estado")
def actualizar_estado(dispositivo_id: str):
    dispositivo = _registro.obtener(dispositivo_id)
    if not dispositivo:
        raise ExcepcionDispositivoNoEncontrado(dispositivo_id)
    payload = request.get_json(silent=True) or {}
    try:
        dispositivo.estado = payload.get("estado", "")
    except ExcepcionConfiguracionInvalida:
        raise
    except (TypeError, AttributeError) as err:
        raise ExcepcionConfiguracionInvalida("Estado no válido.", "estado") from err
    else:
        _persistir()
        return jsonify(dispositivo.to_dict())
    finally:
        pass


@app.post("/api/dispositivos/<dispositivo_id>/diagnostico")
def diagnostico_uno(dispositivo_id: str):
    dispositivo = _registro.obtener(dispositivo_id)
    if not dispositivo:
        raise ExcepcionDispositivoNoEncontrado(dispositivo_id)
    resultado = None
    try:
        resultado = dispositivo.ejecutar_diagnostico()
    except (IndexError, ZeroDivisionError) as err:
        return jsonify({"error": "Error durante diagnóstico simulado."}), 500
    else:
        return jsonify(resultado)
    finally:
        if resultado:
            pass


@app.post("/api/diagnosticos/ejecutar-todos")
def diagnostico_todos():
    try:
        resultados = _registro.diagnosticar_todos()
    except Exception:
        return jsonify({"error": "No se pudo completar el barrido de diagnóstico."}), 500
    else:
        return jsonify(resultados)
    finally:
        pass


@app.post("/api/demo/semilla")
def cargar_semilla():
    """Datos de ejemplo para el laboratorio."""
    if _registro.listar():
        return jsonify({"mensaje": "Ya hay dispositivos registrados.", "count": len(_registro.listar())})
    muestras = [
        {"tipo": "router", "nombre": "R-Core-Lab", "ip": "10.0.0.1", "ubicacion": "Edificio A - Rack 1", "tablas_enrutamiento": 12, "ancho_banda_mbps": 10000},
        {"tipo": "switch", "nombre": "SW-Planta-2", "ip": "10.0.2.10", "ubicacion": "Edificio B - Sala redes", "puertos": 48, "vlan_count": 6},
        {"tipo": "router", "nombre": "R-Borde", "ip": "192.168.100.1", "ubicacion": "DMZ Campus", "estado": "mantenimiento", "tablas_enrutamiento": 8, "ancho_banda_mbps": 2500},
    ]
    for payload in muestras:
        _registro.agregar(RegistroLaboratorio.crear_desde_payload(payload))
    _persistir()
    return jsonify({"mensaje": "Semilla cargada.", "count": len(_registro.listar())})


def create_app() -> Flask:
    return app


if __name__ == "__main__":
    port = int(os.getenv("PORT", "5000"))
    app.run(host="0.0.0.0", port=port, debug=os.getenv("FLASK_DEBUG", "0") == "1")

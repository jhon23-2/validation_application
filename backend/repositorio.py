"""Persistencia JSON simple para el inventario del laboratorio."""

from __future__ import annotations

import json
import os
from pathlib import Path

from excepciones_personalizadas import ExcepcionConfiguracionInvalida
from models import DispositivoRed, RegistroLaboratorio, Router, Switch

_DATA_DIR = Path(__file__).resolve().parent / "data"
_DATA_FILE = _DATA_DIR / "inventario.json"


def _device_from_record(record: dict) -> DispositivoRed:
    tipo = record.get("tipo")
    comunes = {
        "nombre": record["nombre"],
        "ip": record["ip"],
        "ubicacion": record["ubicacion"],
        "estado": record.get("estado", "activo"),
        "dispositivo_id": record["id"],
    }
    detalles = record.get("detalles") or {}
    if tipo == "router":
        return Router(
            **comunes,
            tablas_enrutamiento=detalles.get("tablas_enrutamiento", 4),
            ancho_banda_mbps=detalles.get("ancho_banda_mbps", 1000.0),
        )
    if tipo == "switch":
        return Switch(
            **comunes,
            puertos=detalles.get("puertos", 24),
            vlan_count=detalles.get("vlan_count", 1),
        )
    raise ExcepcionConfiguracionInvalida(f"Tipo desconocido en archivo: {tipo}", "tipo")


class RepositorioInventario:
    def __init__(self, ruta: Path | None = None):
        self._ruta = ruta or _DATA_FILE

    def cargar_registro(self) -> RegistroLaboratorio:
        registro = RegistroLaboratorio()
        if not self._ruta.exists():
            return registro
        try:
            with open(self._ruta, encoding="utf-8") as fh:
                data = json.load(fh)
        except json.JSONDecodeError as err:
            raise ExcepcionConfiguracionInvalida(
                "El archivo de inventario está corrupto.", "inventario"
            ) from err

        for item in data.get("dispositivos", []):
            try:
                registro.agregar(_device_from_record(item))
            except (KeyError, ExcepcionConfiguracionInvalida):
                continue
        return registro

    def guardar_registro(self, registro: RegistroLaboratorio) -> None:
        os.makedirs(self._ruta.parent, exist_ok=True)
        payload = {
            "dispositivos": [d.to_dict() for d in registro.listar()],
        }
        with open(self._ruta, "w", encoding="utf-8") as fh:
            json.dump(payload, fh, indent=2, ensure_ascii=False)

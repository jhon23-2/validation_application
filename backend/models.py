"""Modelo orientado a objetos: dispositivos de un laboratorio de redes."""

from __future__ import annotations

import re
import uuid
from abc import ABC, abstractmethod
from datetime import datetime, timezone

from excepciones_personalizadas import ExcepcionConfiguracionInvalida

_IPV4 = re.compile(
    r"^(?:(?:25[0-5]|2[0-4]\d|[01]?\d?\d)\.){3}"
    r"(?:25[0-5]|2[0-4]\d|[01]?\d?\d)$"
)
_ESTADOS_VALIDOS = frozenset({"activo", "inactivo", "mantenimiento", "falla"})


def _validar_ip(ip: str) -> str:
    ip = ip.strip()
    if not _IPV4.match(ip):
        raise ExcepcionConfiguracionInvalida(
            "La dirección IP debe ser IPv4 válida (ej. 192.168.1.1).", "ip"
        )
    return ip


class DispositivoRed(ABC):
    """Entidad base: equipo de red del campus."""

    def __init__(
        self,
        nombre: str,
        ip: str,
        ubicacion: str,
        estado: str = "activo",
        dispositivo_id: str | None = None,
    ):
        self.__id = dispositivo_id or str(uuid.uuid4())
        self.nombre = nombre
        self.ip = ip
        self.ubicacion = ubicacion
        self.estado = estado
        self.__fecha_registro = datetime.now(timezone.utc)

    @property
    def id(self) -> str:
        return self.__id

    @property
    def nombre(self) -> str:
        return self.__nombre

    @nombre.setter
    def nombre(self, valor: str) -> None:
        valor = (valor or "").strip()
        if len(valor) < 2:
            raise ExcepcionConfiguracionInvalida(
                "El nombre debe tener al menos 2 caracteres.", "nombre"
            )
        self.__nombre = valor

    @property
    def ip(self) -> str:
        return self.__ip

    @ip.setter
    def ip(self, valor: str) -> None:
        self.__ip = _validar_ip(valor)

    @property
    def ubicacion(self) -> str:
        return self.__ubicacion

    @ubicacion.setter
    def ubicacion(self, valor: str) -> None:
        valor = (valor or "").strip()
        if not valor:
            raise ExcepcionConfiguracionInvalida(
                "La ubicación no puede estar vacía.", "ubicacion"
            )
        self.__ubicacion = valor

    @property
    def estado(self) -> str:
        return self.__estado

    @estado.setter
    def estado(self, valor: str) -> None:
        valor = (valor or "").strip().lower()
        if valor not in _ESTADOS_VALIDOS:
            raise ExcepcionConfiguracionInvalida(
                f"Estado inválido. Use uno de: {', '.join(sorted(_ESTADOS_VALIDOS))}.",
                "estado",
            )
        self.__estado = valor

    @property
    def fecha_registro(self) -> datetime:
        return self.__fecha_registro

    @property
    @abstractmethod
    def tipo(self) -> str:
        """Identificador del tipo concreto de dispositivo."""

    @abstractmethod
    def ejecutar_diagnostico(self) -> dict:
        """Diagnóstico polimórfico según el tipo de equipo."""

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "tipo": self.tipo,
            "nombre": self.nombre,
            "ip": self.ip,
            "ubicacion": self.ubicacion,
            "estado": self.estado,
            "fecha_registro": self.fecha_registro.isoformat(),
            "detalles": self._detalles_dict(),
        }

    @abstractmethod
    def _detalles_dict(self) -> dict:
        pass

    def __str__(self) -> str:
        return f"{self.tipo.upper()} [{self.nombre}] @ {self.ip} — {self.estado}"


class Router(DispositivoRed):
    """Router: enrutamiento entre subredes del laboratorio."""

    def __init__(
        self,
        nombre: str,
        ip: str,
        ubicacion: str,
        estado: str = "activo",
        tablas_enrutamiento: int = 4,
        ancho_banda_mbps: float = 1000.0,
        dispositivo_id: str | None = None,
    ):
        super().__init__(nombre, ip, ubicacion, estado, dispositivo_id)
        self.tablas_enrutamiento = tablas_enrutamiento
        self.ancho_banda_mbps = ancho_banda_mbps

    @property
    def tipo(self) -> str:
        return "router"

    @property
    def tablas_enrutamiento(self) -> int:
        return self.__tablas_enrutamiento

    @tablas_enrutamiento.setter
    def tablas_enrutamiento(self, valor: int) -> None:
        try:
            valor = int(valor)
        except (TypeError, ValueError) as err:
            raise ExcepcionConfiguracionInvalida(
                "Las tablas de enrutamiento deben ser un entero.", "tablas_enrutamiento"
            ) from err
        if valor < 1 or valor > 256:
            raise ExcepcionConfiguracionInvalida(
                "Tablas de enrutamiento deben estar entre 1 y 256.", "tablas_enrutamiento"
            )
        self.__tablas_enrutamiento = valor

    @property
    def ancho_banda_mbps(self) -> float:
        return self.__ancho_banda_mbps

    @ancho_banda_mbps.setter
    def ancho_banda_mbps(self, valor: float) -> None:
        try:
            valor = float(valor)
        except (TypeError, ValueError) as err:
            raise ExcepcionConfiguracionInvalida(
                "El ancho de banda debe ser numérico.", "ancho_banda_mbps"
            ) from err
        if valor <= 0:
            raise ExcepcionConfiguracionInvalida(
                "El ancho de banda debe ser mayor que cero.", "ancho_banda_mbps"
            )
        self.__ancho_banda_mbps = valor

    def calcular_ancho_banda_efectivo(self) -> float:
        try:
            factor_estado = {"activo": 1.0, "mantenimiento": 0.5, "inactivo": 0.0, "falla": 0.0}
            return self.ancho_banda_mbps * factor_estado.get(self.estado, 0.0)
        except ZeroDivisionError:
            return 0.0

    def ejecutar_diagnostico(self) -> dict:
        efectivo = self.calcular_ancho_banda_efectivo()
        salud = "óptima" if self.estado == "activo" and efectivo > 0 else "degradada"
        if self.estado == "falla":
            salud = "crítica"
        return {
            "dispositivo": self.nombre,
            "tipo": self.tipo,
            "prueba": "traceroute_simulado",
            "saltos_verificados": min(self.tablas_enrutamiento, 8),
            "ancho_banda_efectivo_mbps": round(efectivo, 2),
            "salud_enlace": salud,
            "mensaje": f"Router {self.nombre}: rutas activas {self.tablas_enrutamiento}.",
        }

    def _detalles_dict(self) -> dict:
        return {
            "tablas_enrutamiento": self.tablas_enrutamiento,
            "ancho_banda_mbps": self.ancho_banda_mbps,
            "ancho_banda_efectivo_mbps": round(self.calcular_ancho_banda_efectivo(), 2),
        }


class Switch(DispositivoRed):
    """Switch: conmutación en capa 2 del laboratorio."""

    def __init__(
        self,
        nombre: str,
        ip: str,
        ubicacion: str,
        estado: str = "activo",
        puertos: int = 24,
        vlan_count: int = 1,
        dispositivo_id: str | None = None,
    ):
        super().__init__(nombre, ip, ubicacion, estado, dispositivo_id)
        self.puertos = puertos
        self.vlan_count = vlan_count

    @property
    def tipo(self) -> str:
        return "switch"

    @property
    def puertos(self) -> int:
        return self.__puertos

    @puertos.setter
    def puertos(self, valor: int) -> None:
        try:
            valor = int(valor)
        except (TypeError, ValueError) as err:
            raise ExcepcionConfiguracionInvalida(
                "El número de puertos debe ser entero.", "puertos"
            ) from err
        if valor < 4 or valor > 128:
            raise ExcepcionConfiguracionInvalida(
                "Puertos permitidos: entre 4 y 128.", "puertos"
            )
        self.__puertos = valor

    @property
    def vlan_count(self) -> int:
        return self.__vlan_count

    @vlan_count.setter
    def vlan_count(self, valor: int) -> None:
        try:
            valor = int(valor)
        except (TypeError, ValueError) as err:
            raise ExcepcionConfiguracionInvalida(
                "VLAN count debe ser entero.", "vlan_count"
            ) from err
        if valor < 1 or valor > self.puertos:
            raise ExcepcionConfiguracionInvalida(
                "VLANs no pueden superar el número de puertos ni ser menor que 1.",
                "vlan_count",
            )
        self.__vlan_count = valor

    def calcular_ancho_banda(self) -> float:
        """Capacidad agregada estimada (1 Gbps por puerto activo simulado)."""
        try:
            if self.puertos == 0:
                raise ZeroDivisionError
            ocupacion = self.vlan_count / self.puertos
            gbps_base = 1.0
            return self.puertos * gbps_base * (1.0 if self.estado == "activo" else 0.25) * (
                0.8 + 0.2 * ocupacion
            )
        except ZeroDivisionError:
            return 0.0

    def ejecutar_diagnostico(self) -> dict:
        capacidad = self.calcular_ancho_banda()
        puertos_activos = max(1, int(self.puertos * 0.85)) if self.estado == "activo" else 0
        return {
            "dispositivo": self.nombre,
            "tipo": self.tipo,
            "prueba": "tabla_mac_simulada",
            "puertos_activos": puertos_activos,
            "vlans_configuradas": self.vlan_count,
            "capacidad_agregada_gbps": round(capacidad, 2),
            "mensaje": f"Switch {self.nombre}: {puertos_activos}/{self.puertos} puertos en uso.",
        }

    def _detalles_dict(self) -> dict:
        return {
            "puertos": self.puertos,
            "vlan_count": self.vlan_count,
            "capacidad_agregada_gbps": round(self.calcular_ancho_banda(), 2),
        }


class RegistroLaboratorio:
    """Fachada para CRUD y pruebas sobre la colección de dispositivos."""

    def __init__(self) -> None:
        self.__dispositivos: dict[str, DispositivoRed] = {}

    def agregar(self, dispositivo: DispositivoRed) -> DispositivoRed:
        self.__dispositivos[dispositivo.id] = dispositivo
        return dispositivo

    def listar(self) -> list[DispositivoRed]:
        return sorted(self.__dispositivos.values(), key=lambda d: d.nombre.lower())

    def obtener(self, dispositivo_id: str) -> DispositivoRed | None:
        return self.__dispositivos.get(dispositivo_id)

    def buscar_dispositivo(self, criterio: str) -> DispositivoRed | None:
        """Busca por UUID completo o por prefijo del id (mín. 4 caracteres)."""
        criterio = (criterio or "").strip()
        if len(criterio) < 4:
            raise ExcepcionConfiguracionInvalida(
                "Indica al menos 4 caracteres del ID para buscar.", "id"
            )
        exacto = self.obtener(criterio)
        if exacto:
            return exacto
        coincidencias = [
            d for d in self.__dispositivos.values() if d.id.startswith(criterio)
        ]
        if len(coincidencias) == 1:
            return coincidencias[0]
        if len(coincidencias) > 1:
            raise ExcepcionConfiguracionInvalida(
                "Hay varios equipos con ese prefijo; escribe más caracteres del ID.",
                "id",
            )
        return None

    def eliminar_dispositivo(self, dispositivo_id: str) -> bool:
        return self.eliminar(dispositivo_id)

    def eliminar(self, dispositivo_id: str) -> bool:
        if dispositivo_id in self.__dispositivos:
            del self.__dispositivos[dispositivo_id]
            return True
        return False

    def actualizar_estado(self, dispositivo_id: str, estado: str) -> DispositivoRed:
        dispositivo = self.obtener(dispositivo_id)
        if not dispositivo:
            raise ExcepcionConfiguracionInvalida(
                f"No existe dispositivo con id: {dispositivo_id}", "id"
            )
        dispositivo.estado = estado
        return dispositivo

    def actualizar_dispositivo(self, dispositivo_id: str, payload: dict) -> DispositivoRed:
        dispositivo = self.obtener(dispositivo_id)
        if not dispositivo:
            raise ExcepcionConfiguracionInvalida(
                f"No existe dispositivo con id: {dispositivo_id}", "id"
            )
        if "nombre" in payload:
            dispositivo.nombre = payload["nombre"]
        if "ip" in payload:
            dispositivo.ip = payload["ip"]
        if "ubicacion" in payload:
            dispositivo.ubicacion = payload["ubicacion"]
        if "estado" in payload:
            dispositivo.estado = payload["estado"]
        if isinstance(dispositivo, Router):
            if "tablas_enrutamiento" in payload:
                dispositivo.tablas_enrutamiento = payload["tablas_enrutamiento"]
            if "ancho_banda_mbps" in payload:
                dispositivo.ancho_banda_mbps = payload["ancho_banda_mbps"]
        elif isinstance(dispositivo, Switch):
            if "puertos" in payload:
                dispositivo.puertos = payload["puertos"]
            if "vlan_count" in payload:
                dispositivo.vlan_count = payload["vlan_count"]
        return dispositivo

    def diagnosticar_todos(self) -> list[dict]:
        return [d.ejecutar_diagnostico() for d in self.listar()]

    @staticmethod
    def crear_desde_payload(payload: dict) -> DispositivoRed:
        tipo = (payload.get("tipo") or "").strip().lower()
        comunes = {
            "nombre": payload.get("nombre", ""),
            "ip": payload.get("ip", ""),
            "ubicacion": payload.get("ubicacion", ""),
            "estado": payload.get("estado", "activo"),
        }
        if tipo == "router":
            return Router(
                **comunes,
                tablas_enrutamiento=payload.get("tablas_enrutamiento", 4),
                ancho_banda_mbps=payload.get("ancho_banda_mbps", 1000.0),
            )
        if tipo == "switch":
            return Switch(
                **comunes,
                puertos=payload.get("puertos", 24),
                vlan_count=payload.get("vlan_count", 1),
            )
        raise ExcepcionConfiguracionInvalida(
            "Tipo de dispositivo debe ser 'router' o 'switch'.", "tipo"
        )

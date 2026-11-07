"""Excepciones del dominio para gestión de dispositivos de red."""


class ExcepcionConfiguracionInvalida(Exception):
    """Parámetros de configuración rechazados por validación de negocio."""

    def __init__(self, mensaje: str, campo: str | None = None):
        self.campo = campo
        super().__init__(mensaje)


class ExcepcionDispositivoNoEncontrado(Exception):
    """No existe un dispositivo con el identificador solicitado."""

    def __init__(self, dispositivo_id: str):
        self.dispositivo_id = dispositivo_id
        super().__init__(f"Dispositivo no encontrado: {dispositivo_id}")

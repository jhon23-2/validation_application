"""
Punto de entrada del sistema: menú de consola (requisito académico) y opción API.

Uso:
  python main.py              → menú interactivo + pruebas POO
  python main.py --serve      → levantar Flask en puerto 5000
  python main.py --demo-poo   → ejecutar pruebas de objetos sin menú
"""

from __future__ import annotations

import argparse
import sys

from excepciones_personalizadas import ExcepcionConfiguracionInvalida
from models import RegistroLaboratorio, Router, Switch
from repositorio import RepositorioInventario


def ejecutar_pruebas_poo() -> None:
    """Demuestra herencia, polimorfismo y excepciones personalizadas."""
    print("\n=== Pruebas POO: laboratorio de redes ===\n")
    registro = RegistroLaboratorio()

    try:
        router = Router("R-Test", "172.16.0.1", "Lab 301", tablas_enrutamiento=6, ancho_banda_mbps=500)
        switch = Switch("SW-Test", "172.16.0.2", "Lab 301", puertos=24, vlan_count=3)
        registro.agregar(router)
        registro.agregar(switch)
    except ExcepcionConfiguracionInvalida as err:
        print(f"Error de configuración: {err}")
    else:
        print("Dispositivos creados correctamente.")
        for d in registro.listar():
            print(f"  • {d}")
    finally:
        print("Bloque de creación finalizado.\n")

    # Conversión errónea de tipos
    try:
        Router("Mal", "no-es-ip", "X", tablas_enrutamiento="abc")
    except ExcepcionConfiguracionInvalida as err:
        print(f"[OK] Excepción capturada (IP/tipo): {err}")
    else:
        print("[FALLO] Debió lanzarse ExcepcionConfiguracionInvalida")
    finally:
        pass

    # Índice fuera de rango simulado en lista
    dispositivos = registro.listar()
    try:
        _ = dispositivos[99]
    except IndexError as err:
        print(f"[OK] IndexError capturado: {err}")
    else:
        print("[FALLO] Debió lanzarse IndexError")
    finally:
        pass

    print("\n--- Polimorfismo: ejecutar_diagnostico() ---\n")
    for dispositivo in registro.listar():
        try:
            diag = dispositivo.ejecutar_diagnostico()
        except (ZeroDivisionError, IndexError) as err:
            print(f"Error en diagnóstico: {err}")
        else:
            print(f"{dispositivo.tipo}: {diag.get('mensaje')}")
        finally:
            pass

    print("\n=== Fin de pruebas POO ===\n")


def _input_opcion(mensaje: str) -> str:
    try:
        return input(mensaje).strip()
    except (EOFError, KeyboardInterrupt):
        print("\nSaliendo...")
        sys.exit(0)


def menu_interactivo(registro: RegistroLaboratorio, repo: RepositorioInventario) -> None:
    while True:
        print(
            """
╔══════════════════════════════════════════════╗
║   GESTIÓN LAB. REDES — Menú principal        ║
╠══════════════════════════════════════════════╣
║  1. Listar dispositivos                      ║
║  2. Registrar router                           ║
║  3. Registrar switch                           ║
║  4. Diagnóstico de un dispositivo             ║
║  5. Diagnóstico de todos (polimorfismo)       ║
║  6. Cambiar estado                           ║
║  7. Eliminar dispositivo                     ║
║  8. Ejecutar pruebas POO                     ║
║  0. Salir y guardar                          ║
╚══════════════════════════════════════════════╝
"""
        )
        op = _input_opcion("Opción: ")
        if op == "0":
            repo.guardar_registro(registro)
            print("Inventario guardado. ¡Hasta luego!")
            break
        if op == "1":
            items = registro.listar()
            if not items:
                print("No hay dispositivos.")
            for d in items:
                print(f"  [{d.id[:8]}…] {d}")
            continue
        if op == "8":
            ejecutar_pruebas_poo()
            continue

        if op == "2":
            try:
                nombre = _input_opcion("Nombre: ")
                ip = _input_opcion("IP: ")
                ubicacion = _input_opcion("Ubicación: ")
                tablas = int(_input_opcion("Tablas enrutamiento: ") or "4")
                bw = float(_input_opcion("Ancho banda (Mbps): ") or "1000")
                dev = Router(nombre, ip, ubicacion, tablas_enrutamiento=tablas, ancho_banda_mbps=bw)
                registro.agregar(dev)
                repo.guardar_registro(registro)
                print(f"Router registrado: {dev}")
            except ExcepcionConfiguracionInvalida as err:
                print(f"Error: {err}")
            except ValueError as err:
                print(f"Entrada numérica inválida: {err}")
            else:
                print("Operación completada.")
            finally:
                pass
            continue

        if op == "3":
            try:
                nombre = _input_opcion("Nombre: ")
                ip = _input_opcion("IP: ")
                ubicacion = _input_opcion("Ubicación: ")
                puertos = int(_input_opcion("Puertos: ") or "24")
                vlans = int(_input_opcion("VLANs: ") or "1")
                dev = Switch(nombre, ip, ubicacion, puertos=puertos, vlan_count=vlans)
                registro.agregar(dev)
                repo.guardar_registro(registro)
                print(f"Switch registrado: {dev}")
            except ExcepcionConfiguracionInvalida as err:
                print(f"Error: {err}")
            except ValueError as err:
                print(f"Entrada numérica inválida: {err}")
            else:
                print("Operación completada.")
            finally:
                pass
            continue

        if op in {"4", "5", "6", "7"}:
            items = registro.listar()
            if not items:
                print("No hay dispositivos.")
                continue
            if op == "5":
                for d in items:
                    print(d.ejecutar_diagnostico())
                continue
            dev_id = _input_opcion("ID del dispositivo (primeros 8 chars visibles en listado): ")
            seleccion = next((d for d in items if d.id.startswith(dev_id) or d.id == dev_id), None)
            if not seleccion:
                print("No encontrado.")
                continue
            if op == "4":
                print(seleccion.ejecutar_diagnostico())
            elif op == "6":
                try:
                    nuevo = _input_opcion("Nuevo estado (activo/inactivo/mantenimiento/falla): ")
                    seleccion.estado = nuevo
                    repo.guardar_registro(registro)
                    print(f"Estado actualizado: {seleccion}")
                except ExcepcionConfiguracionInvalida as err:
                    print(f"Error: {err}")
                finally:
                    pass
            elif op == "7":
                registro.eliminar(seleccion.id)
                repo.guardar_registro(registro)
                print("Eliminado.")
            continue

        print("Opción no válida.")


def main() -> None:
    parser = argparse.ArgumentParser(description="Sistema de gestión — Lab de redes (POO)")
    parser.add_argument("--serve", action="store_true", help="Iniciar API Flask")
    parser.add_argument("--demo-poo", action="store_true", help="Solo pruebas de objetos")
    args = parser.parse_args()

    if args.demo_poo:
        ejecutar_pruebas_poo()
        return

    if args.serve:
        from app import app

        app.run(host="0.0.0.0", port=5000, debug=True)
        return

    repo = RepositorioInventario()
    registro = repo.cargar_registro()
    print("Bienvenido al sistema de gestión del laboratorio de redes.")
    ejecutar_pruebas_poo()
    menu_interactivo(registro, repo)


if __name__ == "__main__":
    main()

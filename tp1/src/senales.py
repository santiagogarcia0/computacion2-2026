"""
Módulo encargado de capturar y procesar las señales de Linux (POSIX Signals) 
enviadas al proceso Padre del monitor de forma segura.
"""

import signal
import json
import time
import os

# Variables globales de control para comunicación async-signal-safe
# Las interrupciones del Kernel solo alteran estas banderas rápidas en memoria
PENDING_RELOAD = False
PENDING_DUMP = False
VERBOSE_MODE = False

# SIGINT dentro del bloque finally en main

def configurar_handlers_globales():
    """
    Registra los manejadores (handlers) para capturar las señales del Kernel de Linux.
    """
    # Asociamos cada señal a su respectiva función de interrupción rápida
    signal.signal(signal.SIGHUP, _handle_sighup)
    signal.signal(signal.SIGUSR1, _handle_sigusr1)
    signal.signal(signal.SIGUSR2, _handle_sigusr2)
    print("[*] Handlers de señales (SIGHUP, SIGUSR1, SIGUSR2) vinculados al Padre.")


def _handle_sighup(signum, frame):
    """Manejador rápido para SIGHUP (Recargar configuración)."""
    global PENDING_RELOAD
    PENDING_RELOAD = True


def _handle_sigusr1(signum, frame):
    """Manejador rápido para SIGUSR1 (Volcado de Snapshot)."""
    global PENDING_DUMP
    PENDING_DUMP = True


def _handle_sigusr2(signum, frame):
    """Manejador rápido para SIGUSR2 (Alternar Modo Verbose)."""
    global VERBOSE_MODE
    VERBOSE_MODE = not VERBOSE_MODE
    # Usamos os.write en lugar de print porque os.write es reentrante y async-signal-safe
    os.write(1, b"\n[Senal] SIGUSR2 recibida. Toggle Modo Verbose.\n")



def procesar_senales_pendientes(snapshot_compartido, intervalos_compartidos):
    """
    Verifica de forma segura y síncrona si hay tareas diferidas por las señales.
    Esta función la llamará el Padre en su bucle principal de control.
    """
    global PENDING_RELOAD, PENDING_DUMP, VERBOSE_MODE
    
    # 1. Resolver SIGHUP pendiente (Recargar config.json)
    if PENDING_RELOAD:
        PENDING_RELOAD = False
        print("\n[*] Procesando SIGHUP de forma segura: Recargando config.json...")
        if os.path.exists("config.json"):
            try:
                with open("config.json", "r", encoding="utf-8") as f:
                    config = json.load(f)
                    
                # Extraemos los nuevos tiempos del JSON
                nuevos_intervalos = config.get("intervalos", {})
                
                # Actualizamos los multiprocessing.Value de la RAM compartida en caliente
                for dimension, value_objeto in intervalos_compartidos.items():
                    if dimension in nuevos_intervalos:
                        viejo = value_objeto.value
                        nuevo = float(nuevos_intervalos[dimension])
                        value_objeto.value = nuevo
                        print(f"     └─ Dimensión [{dimension.upper()}]: Cambió refresco {viejo}s -> {nuevo}s")
                print("[ OK ] Configuración re-aplicada dinámicamente en RAM.")
            except Exception as e:
                print(f"[!] Error al procesar recarga de config.json: {e}")
        else:
            print("[!] Alerta: Archivo config.json no encontrado.")

    # 2. Resolver SIGUSR1 pendiente (Dump JSON del Snapshot)
    if PENDING_DUMP:
        PENDING_DUMP = False
        print("\n[*] Procesando SIGUSR1 de forma segura: Volcando snapshot global a disco...")
        try:
            timestamp = int(time.time())
            nombre_archivo = f"dump_{timestamp}.json"
            
            # El Manager dict no es serializable directamente a JSON porque es un proxy.
            # Debemos convertirlo a un diccionario normal de Python recorriendo sus claves.
            snapshot_plano = {}
            for seccion, datos in snapshot_compartido.items():
                # Para evitar sub-proxies del Manager, guardamos copias planas
                snapshot_plano[seccion] = dict(datos) if isinstance(datos, dict) else datos
                
            with open(nombre_archivo, "w", encoding="utf-8") as f:
                json.dump(snapshot_plano, f, indent=4, ensure_ascii=False)
                
            print(f"[ OK ] Dump generado con éxito en el archivo: {nombre_archivo}")
        except Exception as e:
            print(f"[!] Error al generar el dump del snapshot: {e}")

#!/usr/bin/env python3

"""
Punto de entrada oficial del monitor de procesos.
Lanza los procesos hijos en paralelo y renderiza la interfaz interactiva.
"""
import os
import multiprocessing
import threading
import time
import sys

# Primitivas IPC y constantes
from common.ipc import crear_evento_shutdown, crear_intervalos_compartidos, crear_snapshot
from common.constantes import SECCIONES_SNAPSHOT

# Componentes del sistema
from recolector import ejecutar_recolector
from display import ejecutar_display
import senales

# Los 7 analizadores paralelos
from analizadores.resumen import ejecutar_analizador_resumen
from analizadores.memoria import ejecutar_analizador_memoria
from analizadores.fds import ejecutar_analizador_fds
from analizadores.threads import ejecutar_analizador_threads
from analizadores.senales import ejecutar_analizador_senales
from analizadores.scheduling import ejecutar_analizador_scheduling
from analizadores.sistema import ejecutar_analizador_sistema


def bucle_senales_background(snapshot, intervalos, shutdown_event):
    """Hilo secundario del Padre encargado de vigilar las señales en background."""
    while not shutdown_event.is_set():
        senales.procesar_senales_pendientes(snapshot, intervalos)
        time.sleep(0.5)


def main():
    """ Orquesta la flota completa de procesos paralelos e inicia la TUI principal. """
    # 1. Registrar manejadores de señales async-signal-safe
    senales.configurar_handlers_globales()
    
    manager = multiprocessing.Manager()

    # Reservamos estructuras de datos en la RAM compartida nativa
    snapshot = crear_snapshot(manager)
    intervalos = crear_intervalos_compartidos(manager)
    shutdown_event = crear_evento_shutdown()

    procesos_hijos = []
    
    # Creamos las 7 colas dedicadas para el esquema multiplexado del Recolector
    diccionario_colas = {}
    for seccion in SECCIONES_SNAPSHOT:
        diccionario_colas[seccion] = multiprocessing.Queue()

    # Mapa de asignación de funciones de los analizadores
    mapeo_analizadores = {
        "resumen": ejecutar_analizador_resumen,
        "memoria": ejecutar_analizador_memoria,
        "fds": ejecutar_analizador_fds,
        "threads": ejecutar_analizador_threads,
        "senales": ejecutar_analizador_senales,
        "scheduling": ejecutar_analizador_scheduling,
        "sistema": ejecutar_analizador_sistema
    }

    try:
        # 2. LANZAR PROCESO HIJO: El Recolector Central Multiplexado
        p_recolector = multiprocessing.Process(
            target=ejecutar_recolector,
            args=(diccionario_colas, shutdown_event, 1.0),
            name="Monitor-Recolector"
        )
        p_recolector.start()
        procesos_hijos.append(p_recolector)

        # 3. LANZAR PROCESOS HIJOS: Los 7 Analizadores en paralelo real
        for seccion, funcion_analizador in mapeo_analizadores.items():
            p_hijo = multiprocessing.Process(
                target=funcion_analizador,
                args=(diccionario_colas[seccion], snapshot, intervalos[seccion], shutdown_event),
                name=f"Monitor-Analizador-{seccion.capitalize()}"
            )
            p_hijo.start()
            procesos_hijos.append(p_hijo)

        # 4. LANZAR HILO DE SEÑALES: Vigilante en paralelo del Padre
        hilo_senales = threading.Thread(
            target=bucle_senales_background,
            args=(snapshot, intervalos, shutdown_event),
            daemon=True
        )
        hilo_senales.start()

        # 5. EJECUTAR TUI EN PROCESO PRINCIPAL: Control absoluto de terminal y teclado
        ejecutar_display(snapshot, intervalos, shutdown_event)

    except KeyboardInterrupt:
        pass

    finally:
        # =====================================================================
        # SHUTDOWN LIMPIO Y ORDENADO (Garantía de la materia)
        # =====================================================================
        shutdown_event.set() # Semáforo en rojo para todos los componentes
        
        os.system("clear" if os.name == "posix" else "")
        print("\n=== INICIANDO APAGADO ORDENADO DE LA ARQUITECTURA ===")
        
        for hijo in procesos_hijos:
            hijo.join(timeout=1.0)
            if hijo.is_alive():
                hijo.terminate()
                
        manager.shutdown()
        print("[ OK ] Ecosistema multiproceso cerrado. Recursos liberados. Entrega exitosa.")


if __name__ == "__main__":
    main()

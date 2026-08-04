"""
Primitivas IPC (Inter-Process Communication) utilizadas por el monitor.
"""

from multiprocessing import Manager, Event, Value
from common.constantes import SECCIONES_SNAPSHOT


def crear_snapshot(manager: Manager):
    """
    Crea el snapshot global compartido en la memoria del Manager.
    """
    snapshot = manager.dict()
    for seccion in SECCIONES_SNAPSHOT:
        snapshot[seccion] = {}
    return snapshot


def crear_intervalos_compartidos(manager: Manager):
    """
    Crea las variables dinámicas de tiempo de refresco para cada vista.
    Usamos el Manager de forma genérica o Value nativo.
    """
    # Creamos variables numéricas 'd' (double) en memoria compartida
    intervalos = {
        "resumen": Value('d', 2.0),
        "memoria": Value('d', 3.0),
        "fds": Value('d', 5.0),
        "threads": Value('d', 2.0),
        "senales": Value('d', 10.0),
        "scheduling": Value('d', 10.0),
        "sistema": Value('d', 2.0)
    }
    return intervalos


def crear_evento_shutdown():
    """
    Crea el evento global de apagado (semáforo en verde/rojo).
    """
    return Event()

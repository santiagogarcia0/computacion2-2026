"""Utilidades para trabajar con colas multiproceso de forma robusta."""

import queue
from multiprocessing import Queue


def extraer_pids_de_cola(cola_pids: Queue) -> list[int]:
    """Drena todos los PIDs disponibles en una cola sin depender de empty()."""
    pids = []
    while True:
        try:
            pids.append(cola_pids.get_nowait())
        except queue.Empty:
            break
    return pids

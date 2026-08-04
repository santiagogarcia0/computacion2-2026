"""
Analizador especializado en la dimensión de File Descriptors (FDs).
Se ejecuta en su propio proceso hijo y alimenta la pestaña 'fds' del Snapshot.
"""

import time
from multiprocessing import Queue, Event
import procfs


def ejecutar_analizador_fds(cola_pids: Queue, snapshot_compartido: dict, intervalo_shared, shutdown_event: Event):
    """
    Bucle principal del Analizador de File Descriptors.
    """
    print("[*] Analizador de File Descriptors iniciado en paralelo.")
    
    while not shutdown_event.is_set():
        # Leer intervalo dinámico desde la RAM compartida
        intervalo_actual = intervalo_shared.value
        
        # Sacamos los PIDs de la cola de trabajo dedicada a FDs
        pids_a_procesar = []
        while not cola_pids.empty():
            try:
                pids_a_procesar.append(cola_pids.get_nowait())
            except Exception:
                break
                
        if pids_a_procesar:
            diccionario_fds = {}
            
            for pid in pids_a_procesar:
                # Llamamos a la función nativa que lee os.readlink de /proc/<pid>/fd
                lista_fds_proceso = procfs.leer_fds(pid)
                
                # Guardamos la lista de FDs (aunque esté vacía por falta de permisos)
                diccionario_fds[str(pid)] = {
                    "total_fds": len(lista_fds_proceso),
                    "lista": lista_fds_proceso
                }
            
            # Impactamos el Snapshot Global en su pestaña correspondiente (Acción del Agregador)
            snapshot_compartido["fds"] = {
                "timestamp": time.time(),
                "procesos": diccionario_fds
            }
            
        # Dormir el intervalo dinámico en porciones cortas
        for _ in range(int(intervalo_actual / 0.1)):
            if shutdown_event.is_set():
                break
            time.sleep(0.1)

    print("[*] Analizador de File Descriptors finalizado limpiamente.")

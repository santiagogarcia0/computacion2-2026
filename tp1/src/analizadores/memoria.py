"""
Analizador especializado en la dimensión de Memoria Detallada.
Se ejecuta en su propio proceso hijo y alimenta la pestaña 'memoria' del Snapshot.
"""

import time
from multiprocessing import Queue, Event
import procfs


def ejecutar_analizador_memoria(cola_pids: Queue, snapshot_compartido: dict, intervalo_shared, shutdown_event: Event):
    """
    Bucle principal del Analizador de Memoria.
    """
    print("[*] Analizador de Memoria iniciado en paralelo.")
    
    while not shutdown_event.is_set():
        # Leer intervalo dinámico desde la TUI
        intervalo_actual = intervalo_shared.value
        
        # Sacamos los PIDs de la cola de trabajo compartida
        pids_a_procesar = []
        while not cola_pids.empty():
            try:
                pids_a_procesar.append(cola_pids.get_nowait())
            except Exception:
                break
                
        if pids_a_procesar:
            diccionario_memoria = {}
            
            for pid in pids_a_procesar:
                # Usamos el motor de procfs que ya probamos y funciona
                datos_mem = procfs.leer_memoria_proceso(pid)
                
                # Si el proceso no arrojó datos (porque murió en el camino), lo saltamos
                if not datos_mem or datos_mem["vmsize"] == "0 KB":
                    continue
                    
                # Guardamos la radiografía completa usando el PID como clave string
                diccionario_memoria[str(pid)] = datos_mem
            
            # Guardamos todo el lote consolidado en la pestaña correspondiente (Acción del Agregador)
            snapshot_compartido["memoria"] = {
                "timestamp": time.time(),
                "procesos": diccionario_memoria
            }
            
        # Dormir el intervalo dinámico en porciones cortas para reaccionar rápido al shutdown
        for _ in range(int(intervalo_actual / 0.1)):
            if shutdown_event.is_set():
                break
            time.sleep(0.1)

    print("[*] Analizador de Memoria finalizado limpiamente.")

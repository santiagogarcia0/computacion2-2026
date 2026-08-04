"""
Módulo del componente Recolector.
Se ejecuta en el proceso principal o en un proceso dedicado para distribuir 
el trabajo de escaneo de PIDs a los analizadores mediante colas IPC.
"""

import time
import queue
from multiprocessing import Queue, Event
import procfs


def ejecutar_recolector(cola_pids: Queue, shutdown_event: Event, intervalo_base: float = 1.0):
    """
    Bucle principal del recolector de PIDs.
    
    Mapea el sistema en busca de procesos vivos y los introduce en la cola
    para que los analizadores distribuidos los procesen en paralelo.
    """
    print(f"[*] Recolector central iniciado de forma síncrona.")
    
    while not shutdown_event.is_set():
        try:
            # 1. Obtener la lista fresca de todos los PIDs vivos en Linux
            pids_actuales = procfs.listar_pids()
            
            # 2. Limpieza preventiva de la cola
            # Si los analizadores son más lentos que el recolector, la cola se acumularía con datos viejos. Vaciamos lo que haya quedado antes de inyectar lo nuevo.
            while True:
                try:
                    #Al usar get_nowait(), si la cola está vacía, Python no se queda esperando, lanza inmediatamente una excepción interna llamada queue.Empty
                    cola_pids.get_nowait()
                except queue.Empty:
                    break
            
            # 3. Distribuir los PIDs activos a la cola de trabajo IPC
            # Metemos la lista completa o los PIDs uno por uno. Metiendo la lista completa aseguramos un único viaje atómico por el canal IPC.
            for pid in pids_actuales:
                cola_pids.put(pid)
                
        except Exception as e:
            print(f"[!] Error en el bucle del Recolector: {e}")
            
        # 4. Dormir el intervalo base para no saturar de llamadas al sistema a /proc
        # Hacemos mini-pausas de 0.1s para reaccionar rápido al evento de apagado
        for _ in range(int(intervalo_base / 0.1)):
            if shutdown_event.is_set():
                break
            time.sleep(0.1)

    print("[*] Recolector central finalizado limpiamente.")

"""Analizador especializado en estadísticas globales del Kernel y hardware."""
import time
from multiprocessing import Queue, Event
import procfs
from common.queue_utils import extraer_pids_de_cola

def ejecutar_analizador_sistema(cola_pids: Queue, snapshot_compartido: dict, intervalo_shared, shutdown_event: Event):
    print("[*] Analizador de Sistema Global iniciado en paralelo.")
    while not shutdown_event.is_set():
        intervalo_actual = intervalo_shared.value
        
        # Simplemente vaciamos su cola para que no se sature si el recolector le manda datos
        extraer_pids_de_cola(cola_pids)
                
        # Leemos las estadísticas globales utilizando nuestra nueva función de procfs
        stats_globales = procfs.leer_sistema_global()
        stats_globales["timestamp"] = time.time()
        
        # Impactamos directo en el casillero global
        snapshot_compartido["sistema"] = stats_globales
        
        for _ in range(int(intervalo_actual / 0.1)):
            if shutdown_event.is_set(): break
            time.sleep(0.1)
    print("[*] Analizador de Sistema Global finalizado limpiamente.")

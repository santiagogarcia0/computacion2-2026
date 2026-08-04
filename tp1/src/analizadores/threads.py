"""Analizador especializado en hilos (LWPs)."""
import time
from multiprocessing import Queue, Event
import procfs

def ejecutar_analizador_threads(cola_pids: Queue, snapshot_compartido: dict, intervalo_shared, shutdown_event: Event):
    print("[*] Analizador de Threads iniciado en paralelo.")
    while not shutdown_event.is_set():
        intervalo_actual = intervalo_shared.value
        pids_a_procesar = []
        while not cola_pids.empty():
            try: pids_a_procesar.append(cola_pids.get_nowait())
            except: break
                
        if pids_a_procesar:
            diccionario_threads = {}
            for pid in pids_a_procesar:
                # Reutiliza la función que ya programamos con task/<tid>/stat
                lista_hilos = procfs.leer_threads(pid)
                diccionario_threads[str(pid)] = {
                    "cantidad": len(lista_hilos),
                    "lista": lista_hilos
                }
            snapshot_compartido["threads"] = {"timestamp": time.time(), "procesos": diccionario_threads}
            
        for _ in range(int(intervalo_actual / 0.1)):
            if shutdown_event.is_set(): break
            time.sleep(0.1)
    print("[*] Analizador de Threads finalizado limpiamente.")

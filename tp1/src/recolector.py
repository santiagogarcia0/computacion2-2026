"""
Módulo del componente Recolector Central.
Se ejecuta en su propio proceso hijo para mapear el sistema en busca de PIDs activos
y distribuir la carga de trabajo a todos los analizadores.
"""

import time
import queue
from multiprocessing import Queue, Event
import procfs


def ejecutar_recolector(diccionario_colas: dict[str, Queue], shutdown_event: Event, intervalo_base: float = 1.0):
    """
    Bucle principal del Recolector Central del sistema.
    
    Recibe un diccionario indexado por el nombre de cada sección donde los valores
    son las colas IPC correspondientes a cada proceso analizador hijo.
    """
    print(f"[*] Recolector Central Multiplexado iniciado con PID.")
    print(f"[*] Distribuyendo trabajo hacia las dimensiones: {list(diccionario_colas.keys())}")
    
    while not shutdown_event.is_set():
        try:
            # 1. Escanear la nómina fresca de PIDs activos en el Kernel de Linux
            pids_actuales = procfs.listar_pids()
            
            # 2. Multiplexación y Limpieza: Iteramos por cada cola de cada analizador
            for nombre_dimension, cola_trabajo in diccionario_colas.items():
                
                # Vaciamos de forma preventiva cualquier PID obsoleto de la vuelta anterior
                while True:
                    try:
                        cola_trabajo.get_nowait()
                    except queue.Empty:
                        break
                
                # Inyectamos de forma atómica los PIDs para este analizador específico
                # NOTA: La dimensión "sistema" no usa los PIDs individuales, pero le mandamos
                # la señal para mantener sincronizado el pulso de ejecución.
                for pid in pids_actuales:
                    cola_trabajo.put(pid)
                    
        except Exception as e:
            print(f"[!] Error crítico en el bucle del Recolector Central: {e}")
            
        # 3. Control de Espera Activa fraccionado para reaccionar al Shutdown
        for _ in range(int(intervalo_base / 0.1)):
            if shutdown_event.is_set():
                break
            time.sleep(0.1)

    print("[*] Recolector Central finalizado limpiamente.")

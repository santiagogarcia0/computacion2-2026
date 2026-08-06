"""
Analizador especializado en la dimensión de Resumen.
Se ejecuta en su propio proceso hijo y actualiza el Snapshot Global.
"""

import time
from multiprocessing import Queue, Event
import procfs
from common.constantes import ESTADOS_PROCESO
from common.queue_utils import extraer_pids_de_cola


def ejecutar_analizador_resumen(cola_pids: Queue, snapshot_compartido: dict, intervalo_shared, shutdown_event: Event):
    """
    Bucle principal del Analizador de Resumen.
    """
    print("[*] Analizador de Resumen iniciado en paralelo.")
    cant_cpus = procfs.obtener_cantidad_cpus()
    
    while not shutdown_event.is_set():
        # 1. Obtener el intervalo dinámico que la TUI configuró en la RAM compartida
        intervalo_actual = intervalo_shared.value
        
        # Recolectamos todos los PIDs que estén disponibles en la cola en este momento
        pids_a_procesar = extraer_pids_de_cola(cola_pids)
            
        if pids_a_procesar:
            diccionario_resumen = {}

            # %CPU = ((utime2 + stime2) - (utime1 + stime1)) / ((jiffies2 - jiffies1) * num_cpus) * 100
            # --- MUESTRA A: Captura inicial de Jiffies para el cálculo de CPU% ---
            jiffies_sistema_A = procfs.leer_cpu_global_jiffies()
            jiffies_procesos_A = {}
            for pid in pids_a_procesar:
                campos_stat = procfs.leer_stat_proceso(pid)
                if len(campos_stat) > 14:
                    # Campo 14 (idx 13) es utime, Campo 15 (idx 14) es stime
                    utime = int(campos_stat[13])
                    stime = int(campos_stat[14])
                    jiffies_procesos_A[pid] = utime + stime

            # Esperamos una mini-fracción de tiempo para generar el Delta matemático
            time.sleep(0.2)

            # --- MUESTRA B: Captura final de Jiffies ---
            jiffies_sistema_B = procfs.leer_cpu_global_jiffies()
            delta_sistema = jiffies_sistema_B - jiffies_sistema_A

            # --- EXTRACCIÓN Y AGREGACIÓN ---
            for pid in pids_a_procesar:
                campos_stat = procfs.leer_stat_proceso(pid)
                status_info = procfs.leer_status(pid)
                
                if not campos_stat or not status_info:
                    continue # El proceso murió en el medio
                    
                # Calcular CPU% real
                cpu_porcentaje = 0.0
                if pid in jiffies_procesos_A and len(campos_stat) > 14 and delta_sistema > 0:
                    utime_B = int(campos_stat[13])
                    stime_B = int(campos_stat[14])
                    delta_proceso = (utime_B + stime_B) - jiffies_procesos_A[pid]
                    cpu_porcentaje = (delta_proceso / delta_sistema) * 100.0 * cant_cpus

                # Extraer datos requeridos por la consigna
                letra_estado = campos_stat[2]
                estado_legible = ESTADOS_PROCESO.get(letra_estado, f"Unknown ({letra_estado})")
                
                # Uid viene como "1000  1000  1000  1000" (Real, effective, saved, filesystem), nos quedamos solo con el primero que es el real
                uid_real = status_info.get("Uid", "0").split()[0]

                # Pid en str porque en JSON no se pueden usar claves numéricas, y en la TUI lo vamos a recorrer como diccionario
                diccionario_resumen[str(pid)] = {
                    "pid": pid,
                    "ppid": int(status_info.get("PPid", 0)),
                    "usuario": uid_real, # Después la TUI lo puede traducir a nombre de texto
                    "estado": estado_legible,
                    "comando": procfs.leer_cmdline(pid)[:50], # Recortamos para la vista resumen
                    "cpu_porc": round(cpu_porcentaje, 1),
                    "threads": int(status_info.get("Threads", 1)),
                    "rss": status_info.get("VmRSS", "0 KB")
                }
            
            # 4. IMPACTAR EL SNAPSHOT GLOBAL (Acción del Agregador)
            # Guardamos todo el paquete junto con un timestamp de actualización
            snapshot_compartido["resumen"] = {
                "timestamp": time.time(),
                "procesos": diccionario_resumen
            }

        # 5. Dormir el tiempo restante respetando el intervalo dinámico
        # Descontamos el pequeño sleep de 0.2s que usamos para la muestra de CPU
        tiempo_dormir = max(0.1, intervalo_actual - 0.2)
        for _ in range(int(tiempo_dormir / 0.1)):
            if shutdown_event.is_set():
                break
            time.sleep(0.1)

    print("[*] Analizador de Resumen finalizado limpiamente.")

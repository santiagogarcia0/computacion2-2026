"""Analizador especializado en prioridades, nice y contextos del planificador."""
import time
from multiprocessing import Queue, Event
import procfs
from common.queue_utils import extraer_pids_de_cola

def ejecutar_analizador_scheduling(cola_pids: Queue, snapshot_compartido: dict, intervalo_shared, shutdown_event: Event):
    print("[*] Analizador de Scheduling iniciado en paralelo.")
    while not shutdown_event.is_set():
        intervalo_actual = intervalo_shared.value
        pids_a_procesar = extraer_pids_de_cola(cola_pids)
                
        if pids_a_procesar:
            diccionario_sched = {}
            for pid in pids_a_procesar:
                campos_stat = procfs.leer_stat_proceso(pid)
                status_info = procfs.leer_status(pid)
                if len(campos_stat) > 19 and status_info:
                    diccionario_sched[str(pid)] = {
                        "prioridad": campos_stat[17], # Campo 18 de stat
                        "nice": campos_stat[18],      # Campo 19 de stat
                        "politica": campos_stat[40] if len(campos_stat) > 40 else "OTHER",
                        "ctx_voluntarios": status_info.get("voluntary_ctxt_switches", "0"),
                        "ctx_involuntarios": status_info.get("nonvoluntary_ctxt_switches", "0")
                    }
            snapshot_compartido["scheduling"] = {"timestamp": time.time(), "procesos": diccionario_sched}
            
        for _ in range(int(intervalo_actual / 0.1)):
            if shutdown_event.is_set(): break
            time.sleep(0.1)
    print("[*] Analizador de Scheduling finalizado limpiamente.")

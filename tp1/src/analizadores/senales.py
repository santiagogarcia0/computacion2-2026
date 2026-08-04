"""Analizador especializado en decodificar máscaras de señales del proceso."""
import time
from multiprocessing import Queue, Event
import procfs

def ejecutar_analizador_senales(cola_pids: Queue, snapshot_compartido: dict, intervalo_shared, shutdown_event: Event):
    print("[*] Analizador de Señales iniciado en paralelo.")
    while not shutdown_event.is_set():
        intervalo_actual = intervalo_shared.value
        pids_a_procesar = []
        while not cola_pids.empty():
            try: pids_a_procesar.append(cola_pids.get_nowait())
            except: break
                
        if pids_a_procesar:
            diccionario_senales = {}
            for pid in pids_a_procesar:
                status_info = procfs.leer_status(pid)
                if status_info:
                    # Extraemos las máscaras de 64 bits en formato hexadecimal y las decodificamos
                    diccionario_senales[str(pid)] = {
                        "bloqueadas": procfs.decodificar_mascara_senales(status_info.get("SigBlk", "")),
                        "ignoradas": procfs.decodificar_mascara_senales(status_info.get("SigIgn", "")),
                        "capturadas": procfs.decodificar_mascara_senales(status_info.get("SigCgt", "")),
                        "pendientes": procfs.decodificar_mascara_senales(status_info.get("SigPnd", ""))
                    }
            snapshot_compartido["senales"] = {"timestamp": time.time(), "procesos": diccionario_senales}
            
        for _ in range(int(intervalo_actual / 0.1)):
            if shutdown_event.is_set(): break
            time.sleep(0.1)
    print("[*] Analizador de Señales finalizado limpiamente.")

#!/usr/bin/env python3

"""
Punto de entrada principal del monitor de procesos.
"""
import os as sistema_os
import multiprocessing
import time

# Importamos tus funciones de inicialización IPC
from common.ipc import crear_evento_shutdown, crear_intervalos_compartidos, crear_snapshot

# Importamos el motor de lectura nativo y los nuevos componentes
import procfs
from recolector import ejecutar_recolector
from analizadores.resumen import ejecutar_analizador_resumen


def main():
    """
    Inicialización principal, pruebas de campo y lanzamiento concurrente.
    """
    print("=== INICIALIZANDO ENTORNO MULTIPROCESO ===")
    
    manager = multiprocessing.Manager()

    snapshot = crear_snapshot(manager)
    intervalos = crear_intervalos_compartidos(manager)
    shutdown_event = crear_evento_shutdown()

    print("[*] Estructuras IPC mapeadas en memoria exitosamente.\n")

    # =========================================================================
    # PRUEBA SECUENCIAL ORIGINAL (Para verificar lectura)
    print("=== LECTURA EN TIEMPO REAL DE PROCFS (PRUEBA SECUENCIAL) ===")
    lista_pids = procfs.listar_pids()
    print(f"[*] Procesos vivos detectados en Linux: {len(lista_pids)}")
    
    mi_pid = sistema_os.getpid()
    muestra_pids = [mi_pid] + [p for p in lista_pids if p != mi_pid][:2]
    print(f"[*] Analizando estructura interna de los PIDs de la muestra: {muestra_pids}\n")

    for pid in muestra_pids:
        print(f"--- Datos del Proceso PID: {pid} ---")
        status_info = procfs.leer_status(pid)
        ppid = status_info.get("PPid", "Desconocido")
        threads = status_info.get("Threads", "Desconocido")
        cmdline = procfs.leer_cmdline(pid)
        comando_legible = cmdline if cmdline else "[Kernel Process / Background]"

        stat_campos = procfs.leer_stat_proceso(pid)
        estado_letra = stat_campos[2] if len(stat_campos) > 2 else "?"

        print(f" -> PID Padre (PPID): {ppid}")
        print(f" -> Cantidad de Threads: {threads}")
        print(f" -> Letra de Estado en Kernel: '{estado_letra}'")
        print(f" -> Comando Ejecutado: {comando_legible}")

        fds_abiertos = procfs.leer_fds(pid)
        print(f" -> FDs Abiertos detectados: {len(fds_abiertos)}")
        for fd_info in fds_abiertos[:2]:
            print(f"     [FD {fd_info['fd']}] Tipo: {fd_info['tipo']} -> {fd_info['destino']}")

        mem_info = procfs.leer_memoria_proceso(pid)
        print(f" -> Memoria Física Real (RSS): {mem_info['vmrss']} | Pico Histórico (HWM): {mem_info['vmhwm']}")
        print(f" -> Segmentos de Memoria Calculados (Bytes):")
        print(f"     [Código/Text]: {mem_info['segmentos']['text']} B")
        print(f"     [Variables/Data]: {mem_info['segmentos']['data']} B")
        print(f"     [Dinámica/Heap]: {mem_info['segmentos']['heap']} B")
        print(f"     [Llamadas/Stack]: {mem_info['segmentos']['stack']} B")
        print("-" * 40)

    print("\n[ OK ] Pruebas secuenciales listas. Arrancando motores en paralelo...")
    print("=" * 60)

    # =========================================================================
    # APARTADO MULTIPROCESO REAL (Lanzamiento de Hijos)
    procesos_hijos = []
    cola_pids_compartida = multiprocessing.Queue()

    try:
        # 1. Lanzamos el proceso hijo Recolector
        p_recolector = multiprocessing.Process(
            target=ejecutar_recolector,
            args=(cola_pids_compartida, shutdown_event, 1.0),
            name="Monitor-Recolector"
        )
        p_recolector.start()
        procesos_hijos.append(p_recolector)
        print(f"[+] Hijo [Recolector] corriendo en PID: {p_recolector.pid}")

        # 2. Lanzamos el proceso hijo Analizador de Resumen
        p_resumen = multiprocessing.Process(
            target=ejecutar_analizador_resumen,
            args=(cola_pids_compartida, snapshot, intervalos["resumen"], shutdown_event),
            name="Monitor-Analizador-Resumen"
        )
        p_resumen.start()
        procesos_hijos.append(p_resumen)
        print(f"[+] Hijo [Analizador Resumen] corriendo en PID: {p_resumen.pid}\n")

        print("=== ESCUCHANDO SNAPSHOT COMPARTIDO EN TIEMPO REAL ===")
        print("El proceso Padre vigila la RAM. Presioná [Ctrl + C] para salir...\n")

        # El padre espía la RAM compartida 4 veces para ver cómo el hijo escribe de verdad
        for i in range(1, 5):
            time.sleep(2.0)
            datos_resumen = snapshot.get("resumen", {})
            procesos_mapeados = datos_resumen.get("procesos", {})
            
            print(f"[Lectura Padre - Muestra {i}/4] Procesos totales en el Snapshot: {len(procesos_mapeados)}")
            if procesos_mapeados:
                # Mostramos los dos primeros procesos que metió el hijo en la RAM
                ejemplos = list(procesos_mapeados.keys())[:2]
                for p_id in ejemplos:
                    inf = procesos_mapeados[p_id]
                    print(f"    │ PID {p_id} │ CPU: {inf['cpu_porc']}% │ RAM: {inf['rss']} │ Estado: {inf['estado']}")
            print("-" * 60)

    except KeyboardInterrupt:
        print("\n\n[!] Cierre solicitado por el usuario (Ctrl+C).")

    finally:
        print("\n=== INICIANDO APAGADO ORDENADO DEL SISTEMA ===")
        shutdown_event.set()  # Le avisa a los hijos que salgan del bucle
        
        for hijo in procesos_hijos:
            print(f"[*] Esperando que cierre el proceso {hijo.name}...")
            hijo.join(timeout=2.0)
            if hijo.is_alive():
                print(f"[!] {hijo.name} colgado, forzando terminación.")
                hijo.terminate()

        manager.shutdown()
        print("[*] Recursos liberados limpiamente. Fin del programa.")


if __name__ == "__main__":
    main()

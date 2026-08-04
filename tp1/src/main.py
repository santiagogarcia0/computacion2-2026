#!/usr/bin/env python3

"""
Punto de entrada principal del monitor de procesos.
Coordina la inicialización IPC, el ciclo secuencial inicial y el despliegue paralelo.
"""
import os as sistema_os
import multiprocessing
import time

# Importamos tus funciones de inicialización IPC
from common.ipc import crear_evento_shutdown, crear_intervalos_compartidos, crear_snapshot

# Importamos el motor de lectura nativo
import procfs

# Importamos el recolector central
from recolector import ejecutar_recolector

# Importamos los dos analizadores que tenemos listos hasta ahora
from analizadores.resumen import ejecutar_analizador_resumen
from analizadores.memoria import ejecutar_analizador_memoria


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
    # TU PRUEBA SECUENCIAL ORIGINAL (Para verificar lectura)
    # =========================================================================
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
    # =========================================================================
    procesos_hijos = []
    
    # IMPORTANTE: Creamos DOS colas independientes.
    # Como tenemos 2 analizadores compitiendo por los datos, si usáramos una sola cola,
    # el de resumen sacaría un PID y el de memoria se quedaría sin ese proceso para analizar.
    # Cada dimensión debe recibir la lista completa de PIDs para mapear su especialidad.
    cola_resumen = multiprocessing.Queue()
    cola_memoria = multiprocessing.Queue()

    try:
        # 1. Lanzamos el proceso hijo Recolector (Le pasamos ambas colas en una lista/tupla)
        # Nota: Ajustamos conceptualmente para que alimente las dos vías de trabajo paralelas
        def recolector_dual(q1, q2, ev, int_b):
            """Función auxiliar temporal para clonar los PIDs en ambas colas."""
            while not ev.is_set():
                pids = procfs.listar_pids()
                for q in [q1, q2]:
                    while not q.empty():
                        try: q.get_nowait()
                        except: break
                    for p in pids: q.put(p)
                time.sleep(int_b)

        p_recolector = multiprocessing.Process(
            target=recolector_dual,
            args=(cola_resumen, cola_memoria, shutdown_event, 1.0),
            name="Monitor-Recolector"
        )
        p_recolector.start()
        procesos_hijos.append(p_recolector)
        print(f"[+] Hijo [Recolector] corriendo en PID: {p_recolector.pid}")

        # 2. Lanzamos el proceso hijo Analizador de Resumen
        p_resumen = multiprocessing.Process(
            target=ejecutar_analizador_resumen,
            args=(cola_resumen, snapshot, intervalos["resumen"], shutdown_event),
            name="Monitor-Analizador-Resumen"
        )
        p_resumen.start()
        procesos_hijos.append(p_resumen)
        print(f"[+] Hijo [Analizador Resumen] corriendo en PID: {p_resumen.pid}")

        # 3. Lanzamos el NUEVO proceso hijo Analizador de Memoria
        p_memoria = multiprocessing.Process(
            target=ejecutar_analizador_memoria,
            args=(cola_memoria, snapshot, intervalos["memoria"], shutdown_event),
            name="Monitor-Analizador-Memoria"
        )
        p_memoria.start()
        procesos_hijos.append(p_memoria)
        print(f"[+] Hijo [Analizador Memoria] corriendo en PID: {p_memoria.pid}\n")

        print("=== ESCUCHANDO SNAPSHOT COMPARTIDO EN TIEMPO REAL ===")
        print("El proceso Padre vigila la RAM. Presioná [Ctrl + C] para salir...\n")

        # El padre vigila la RAM compartida 4 veces para ver cómo cooperan los hijos
        for i in range(1, 5):
            time.sleep(2.5) # Le damos un poquito más de tiempo para que ambos hijos impacten
            
            datos_resumen = snapshot.get("resumen", {}).get("procesos", {})
            datos_memoria = snapshot.get("memoria", {}).get("procesos", {})
            
            print(f"[Lectura Padre - Muestra {i}/4]")
            print(f" -> PIDs en sección Resumen: {len(datos_resumen)} | PIDs en sección Memoria: {len(datos_memoria)}")
            
            if datos_resumen and datos_memoria: # contienen datos?
                # Agarramos un PID testigo que esté en ambas secciones (por ejemplo, tu propio PID)
                pid_testigo = str(mi_pid)
                if pid_testigo in datos_resumen and pid_testigo in datos_memoria:
                    r_info = datos_resumen[pid_testigo]
                    m_info = datos_memoria[pid_testigo]
                    
                    print(f"    [PROCESO TESTIGO PID {pid_testigo}] ({r_info['comando']})")
                    print(f"    ├─ Resumen ──> CPU: {r_info['cpu_porc']}% | Estado: {r_info['estado']}")
                    print(f"    └─ Memoria ──> RSS: {r_info['rss']} | Segmento Heap: {m_info['segmentos']['heap']} Bytes")
            else:
                print("    [...] Esperando sincronización de los analizadores paralelos...")
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

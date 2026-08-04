"""
Módulo encargado de interactuar directamente con el sistema de archivos /proc de Linux.
Extrae información cruda y la transforma en estructuras de datos de Python.
"""

import os
import re
from typing import Any

def listar_pids() -> list[int]:
    """
    Recorre la carpeta /proc y devuelve una lista con todos los PIDs 
    (identificadores de procesos) activos en el sistema.
    
    ¿Cómo funciona? En Linux, cada proceso vivo tiene una carpeta con su 
    número de PID dentro de /proc (ej: /proc/1, /proc/540). Esta función 
    lista los elementos y filtra solo aquellos que sean puramente numéricos.
    """
    pids = []
    try:
        # os.listdir actúa igual que el comando 'ls' de Linux
        for nombre_archivo in os.listdir("/proc"):
            # Si el nombre de la carpeta son solo números, es un proceso vivo
            if nombre_archivo.isdigit():
                pids.append(int(nombre_archivo))
    except PermissionError:
        # En Docker o sistemas reales puede haber carpetas restringidas
        pass
    except FileNotFoundError:
        # Por si el proceso desaparece justo en la milésima de segundo que leemos
        pass
    return pids

def leer_status(pid: int) -> dict[str, str]:
    """
    Lee el archivo /proc/<pid>/status y extrae datos clave en formato Clave: Valor.
    Sirve para obtener: PPid, Uid, Gid, Threads, y máscaras de señales (SigBlk, etc.).
    """
    datos_status = {}
    ruta = f"/proc/{pid}/status"
    
    if not os.path.exists(ruta):
        return datos_status

    try:
        with open(ruta, "r", encoding="utf-8", errors="ignore") as f:
            for linea in f:
                # Cada línea es del estilo "PPid:\t1234"
                if ":" in linea:
                    clave, valor = linea.split(":", 1)
                    # Limpiamos espacios en blanco y tabulaciones molestas (\t o \n)
                    datos_status[clave.strip()] = valor.strip()
    except (FileNotFoundError, ProcessLookupError):
        # El proceso terminó mientras lo leíamos
        pass
        
    return datos_status

def leer_cmdline(pid: int) -> str:
    """
    Lee el archivo /proc/<pid>/cmdline para obtener el comando completo que lanzó el proceso.
    
    ¿Cuál es el truco acá? Linux separa los argumentos de la línea de comandos 
    con el byte nulo ('\x00') en lugar de espacios. Si no lo limpiamos, la TUI se rompe.
    """
    ruta = f"/proc/{pid}/cmdline"
    if not os.path.exists(ruta):
        return ""

    try:
        with open(ruta, "r", encoding="utf-8", errors="ignore") as f:
            contenido = f.read()
            # Reemplazamos los bytes nulos por espacios tradicionales y limpiamos los extremos
            comando = contenido.replace("\x00", " ").strip()
            # Si el proceso no tiene cmdline (pasa con los hilos del Kernel), devolvemos vacío
            return comando if comando else ""
    except (FileNotFoundError, ProcessLookupError):
        return ""

def leer_stat_proceso(pid: int) -> list[str]:
    """
    Lee el archivo /proc/<pid>/stat. Este archivo contiene una sola línea 
    gigante con más de 50 campos separados por espacios que detallan el 
    estado matemático del proceso (jiffies de CPU, prioridad, nice, etc.).
    """
    ruta = f"/proc/{pid}/stat"
    if not os.path.exists(ruta):
        return []

    try:
        with open(ruta, "r", encoding="utf-8", errors="ignore") as f:
            linea = f.read().strip()
            
            # ATENCIÓN: El nombre del comando viene entre paréntesis: (mi_programa)
            # Si el nombre del comando tiene espacios adentro, un .split(" ") rompería los índices.
            # Usamos una expresión regular para aislar el comando y partir correctamente el resto.
            match = re.match(r"^(\d+) \((.+)\) (.+)$", linea)
            if match:
                pid_num = match.group(1)
                comm = match.group(2)
                resto_campos = match.group(3).split(" ")
                
                # Devolvemos una lista armada simulando los índices oficiales de Linux:
                # Campo 1 (índice 0) = PID
                # Campo 2 (índice 1) = Comando corto
                # Campo 3 (índice 2) = Estado
                # A partir de ahí, concatenamos el resto. El campo 14 será el índice 13.
                return [pid_num, comm] + resto_campos
    except (FileNotFoundError, ProcessLookupError):
        pass
        
    return []

def leer_fds(pid: int) -> list[dict[str, str]]:
    """
    Recorre la carpeta /proc/<pid>/fd/ para listar todos los File Descriptors 
    abiertos por el proceso, identificando sus destinos y tipos.
    
    Devuelve una lista de diccionarios, donde cada uno representa un FD.
    """
    lista_fds = []
    ruta_fd = f"/proc/{pid}/fd"
    
    if not os.path.exists(ruta_fd):
        return lista_fds

    try:
        # os.listdir nos da los números de los FDs abiertos (ej: ["0", "1", "2", "3"])
        for fd_num in os.listdir(ruta_fd):
            ruta_simbolica = os.path.join(ruta_fd, fd_num)
            
            try:
                # os.readlink lee a dónde apunta realmente ese acceso directo del Kernel
                destino = os.readlink(ruta_simbolica)
                
                # Inferimos el tipo según lo que contenga la ruta de destino
                if destino.startswith("socket:"):
                    tipo = "Socket (Red)"
                elif destino.startswith("pipe:"):
                    tipo = "Pipe (IPC)"
                elif destino.startswith("/dev/pts/") or destino.startswith("/dev/tty"):
                    tipo = "Terminal (TTY)"
                elif destino.startswith("/"):
                    tipo = "Archivo / Librería"
                else:
                    tipo = "Desconocido / Anon"
                    
                lista_fds.append({
                    "fd": fd_num,
                    "destino": destino,
                    "tipo": tipo
                })
                
            except (FileNotFoundError, ProcessLookupError):
                # El FD se cerró en medio de la lectura
                continue
    except PermissionError:
        # Hay procesos del sistema (como root) que no te dejarán espiar sus FDs
        pass
        
    return lista_fds

def leer_memoria_proceso(pid: int) -> dict[str, Any]:
    """
    Lee /proc/<pid>/status (VmSize, VmRSS, etc.) y /proc/<pid>/maps (Text, data, heap, stack) para consolidar
    todas las métricas de memoria y segmentos del proceso.
    """
    datos_memoria = {
        "vmsize": "0 KB", "vmrss": "0 KB", "vmdata": "0 KB",
        "vmstk": "0 KB", "vmexe": "0 KB", "vmlib": "0 KB",
        "vmhwm": "0 KB", "vmswap": "0 KB",
        "segmentos": {"text": 0, "data": 0, "heap": 0, "stack": 0, "shared": 0}
    }
    
    # 1. Extraer métricas del archivo status
    status_info = leer_status(pid)
    if status_info:
        # Mapeamos las claves oficiales de Linux a nuestro diccionario
        for clave_linux, clave_nuestra in [
            ("VmSize", "vmsize"), ("VmRSS", "vmrss"), ("VmData", "data"),
            ("VmStk", "vmstk"), ("VmExe", "vmexe"), ("VmLib", "vmlib"),
            ("VmHWM", "vmhwm"), ("VmSwap", "vmswap")
        ]:
            if clave_linux in status_info:
                datos_memoria[clave_nuestra] = status_info[clave_linux]

    # 2. Analizar segmentos en /proc/<pid>/maps
    ruta_maps = f"/proc/{pid}/maps"
    if os.path.exists(ruta_maps):
        try:
            with open(ruta_maps, "r", encoding="utf-8", errors="ignore") as f:
                for linea in f:
                    # Cada línea es: "00400000-00452000 r-xp 00000000 08:02 65534 /bin/cat"
                    partes = linea.strip().split(maxsplit=5)
                    if len(partes) < 2:
                        continue
                    
                    # Al usar int(..., 16), le indicás a Python que traduzca ese texto hexadecimal (base 16) a un número entero tradicional de base 10. Restando el final menos el inicio, obtenés cuántos bytes reales mide ese bloque exacto de memoria.
                    rango_memoria = partes[0].split("-")
                    inicio = int(rango_memoria[0], 16)
                    fin = int(rango_memoria[1], 16)
                    tamanio_bytes = fin - inicio
                    
                    permisos = partes[1] # Ejemplo: "r-xp" o "rw-p"
                    
                    # El campo 6 (índice 5) nos dice la etiqueta si existe ([heap], [stack], etc.)
                    etiqueta = partes[5] if len(partes) == 6 else ""
                    
                    # el espacio de direcciones de un proceso puede tener múltiples mapas dispersos que corresponden al mismo tipo de segmento, por eso +=.
                    if "[heap]" in etiqueta:
                        datos_memoria["segmentos"]["heap"] += tamanio_bytes
                    elif "[stack]" in etiqueta:
                        datos_memoria["segmentos"]["stack"] += tamanio_bytes
                    elif "x" in permisos:
                        # Si tiene permiso de ejecución 'x', es código puro (segmento Text)
                        datos_memoria["segmentos"]["text"] += tamanio_bytes
                    elif "w" in permisos and "s" in permisos:
                        # 's' significa compartido (Shared memory)
                        datos_memoria["segmentos"]["shared"] += tamanio_bytes
                    elif "w" in permisos:
                        # Escritura pero no ejecutable ni compartido, son variables (Data)
                        datos_memoria["segmentos"]["data"] += tamanio_bytes
                        
        except (FileNotFoundError, ProcessLookupError, PermissionError):
            pass

    return datos_memoria

def leer_cpu_global_jiffies() -> int:
    """Devuelve la suma de todos los jiffies de la línea 'cpu' de /proc/stat."""
    try:
        with open("/proc/stat", "r") as f:
            #cpu 15204 302 5421 984520 ... (este formato)
            primera_linea = f.readline()
            if primera_linea.startswith("cpu"):
                # Separamos los números de la línea cpu: user, nice, system, idle, etc.
                partes = primera_linea.strip().split()
                # Sumamos todos los campos numéricos para obtener el tiempo total del sistema
                return sum(int(x) for x in partes[1:])
    except Exception:
        pass
    return 0

def obtener_cantidad_cpus() -> int:
    """Devuelve la cantidad de núcleos de CPU activos leyendo /proc/cpuinfo."""
    try:
        with open("/proc/cpuinfo", "r") as f:
            contenido = f.read()
            # Contamos cuántas veces aparece la palabra 'processor' (mínimo 1 vez)
            return max(1, contenido.count("processor"))
    except Exception:
        return 1

import signal

def decodificar_mascara_senales(mascara_hex: str) -> list[str]:
    """
    Toma una máscara hexadecimal de 64 bits (ej: '0000000000000004') y devuelve
    una lista con los nombres de las señales activas (ej: ['SIGINT']).
    """
    if not mascara_hex:
        return []
    try:
        # Convertimos el string hexadecimal a un número entero
        mascara_int = int(mascara_hex, 16)
    except ValueError:
        return []
        
    senales_activas = []
    # Recorremos los primeros 32 bits de señales estándar de Linux
    for signum in range(1, 32):
        # Evaluamos bit por bit usando desplazamiento y operación AND Para saber si una señal específica está encendida
        if (mascara_int >> (signum - 1)) & 1:
            try:
                # Obtenemos el nombre oficial del módulo signal (ej: 2 -> 'SIGINT')
                nombre = signal.Signals(signum).name #
                senales_activas.append(nombre)
            except ValueError:
                senales_activas.append(f"SIG_{signum}")
    return senales_activas

def leer_sistema_global() -> dict[str, Any]:
    """Lee /proc/meminfo y /proc/loadavg para obtener las métricas globales del sistema."""
    stats = {"mem_total": "0 KB", "mem_libre": "0 KB", "load_avg": "0.0 0.0 0.0"}
    
    # 1. Leer Memoria Global
    if os.path.exists("/proc/meminfo"):
        try:
            with open("/proc/meminfo", "r") as f:
                for linea in f:
                    if linea.startswith("MemTotal:"):
                        stats["mem_total"] = linea.split(":", 1)[1].strip()
                    elif linea.startswith("MemFree:"):
                        stats["mem_libre"] = linea.split(":", 1)[1].strip()
        except Exception: pass
        
    # 2. Leer Carga de Trabajo (Load Average)
    if os.path.exists("/proc/loadavg"):
        try:
            with open("/proc/loadavg", "r") as f:
                stats["load_avg"] = f.read().strip().split()[:3]
        except Exception: pass
        
    return stats


"""
Módulo del componente Display (TUI) Interactivo Completo y Definitivo.
Renderiza la interfaz y procesa el 100% de los desgloses visuales de las 7 vistas.
[PARTE 1 DE 2 - ARQUITECTURA INDEX REPARADO]
"""

import time
import os
import sys
import select
from multiprocessing import Event
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.layout import Layout
from rich.live import Live

if os.name == "nt":
    import msvcrt

console = Console()

def verificar_teclado() -> str:
    """Lee una tecla desde la entrada estándar de forma no bloqueante y compatible con Windows/WSL."""
    try:
        if os.name == "nt":
            if msvcrt.kbhit():
                tecla = msvcrt.getwch()
                return tecla.lower()
            return ""

        if not sys.stdin.isatty():
            return ""

        rlist, _, _ = select.select([sys.stdin], [], [], 0.0)
        if rlist:
            return sys.stdin.read(1).lower()
    except Exception:
        pass
    return ""

def obtener_datos_vista(snapshot_compartido: dict, vista_activa: str, lista_procesados: list):
    """Selecciona un PID de referencia y los datos de la vista activa de forma robusta."""
    cajon_activo = snapshot_compartido.get(vista_activa, {})
    proc_seccion = cajon_activo.get("procesos", {})

    if vista_activa == "sistema":
        return None, None, proc_seccion, cajon_activo

    if lista_procesados:
        for proceso in lista_procesados:
            pid_str = str(proceso["pid"])
            if pid_str in proc_seccion:
                return pid_str, proc_seccion[pid_str], proc_seccion, cajon_activo

    if proc_seccion:
        pid_testigo = next(iter(proc_seccion.keys()))
        return pid_testigo, proc_seccion[pid_testigo], proc_seccion, cajon_activo

    return None, None, proc_seccion, cajon_activo


def construir_texto_resumen(pid_testigo_str: str, datos_p_res: dict) -> str:
    texto = f"[bold yellow]RESUMEN DEL PROCESO PID {pid_testigo_str}[/bold yellow]\n\n"
    texto += f"  [cyan]• PID:[/cyan] {datos_p_res.get('pid', pid_testigo_str)}\n"
    texto += f"  [cyan]• PPID:[/cyan] {datos_p_res.get('ppid', 'N/A')}\n"
    texto += f"  [cyan]• UID:[/cyan] {datos_p_res.get('usuario', 'N/A')}\n"
    texto += f"  [cyan]• Estado:[/cyan] {datos_p_res.get('estado', 'N/A')}\n"
    texto += f"  [cyan]• Threads:[/cyan] {datos_p_res.get('threads', 'N/A')}\n"
    texto += f"  [cyan]• CPU:[/cyan] {datos_p_res.get('cpu_porc', 0.0)}%\n"
    texto += f"  [cyan]• RSS:[/cyan] {datos_p_res.get('rss', 'N/A')}\n"
    texto += f"  [cyan]• Comando:[/cyan] {datos_p_res.get('comando', 'N/A')}"
    return texto


def construir_texto_memoria(pid_testigo_str: str, datos_pid: dict) -> str:
    seg = datos_pid.get("segmentos", {})
    texto = f"[bold yellow]MEMORIA DEL PROCESO PID {pid_testigo_str}[/bold yellow]\n\n"
    texto += f"  [cyan]• VmSize:[/cyan] {datos_pid.get('vmsize', 'N/A')}\n"
    texto += f"  [cyan]• VmRSS:[/cyan] {datos_pid.get('vmrss', 'N/A')}\n"
    texto += f"  [cyan]• VmData:[/cyan] {datos_pid.get('vmdata', 'N/A')}\n"
    texto += f"  [cyan]• VmStk:[/cyan] {datos_pid.get('vmstk', 'N/A')}\n"
    texto += f"  [cyan]• VmExe:[/cyan] {datos_pid.get('vmexe', 'N/A')}\n"
    texto += f"  [cyan]• VmLib:[/cyan] {datos_pid.get('vmlib', 'N/A')}\n"
    texto += f"  [cyan]• VmHWM:[/cyan] {datos_pid.get('vmhwm', 'N/A')}\n"
    texto += f"  [cyan]• VmSwap:[/cyan] {datos_pid.get('vmswap', 'N/A')}\n"
    texto += f"  [cyan]• Faults:[/cyan] {datos_pid.get('page_faults', 'N/A')}\n"
    texto += f"  [cyan]• Segmentos text/data/heap/stack/shared:[/cyan] {seg.get('text', 0)}/{seg.get('data', 0)}/{seg.get('heap', 0)}/{seg.get('stack', 0)}/{seg.get('shared', 0)}"
    return texto


def construir_texto_fds(pid_testigo_str: str, datos_pid: dict) -> str:
    texto = f"[bold yellow]FILE DESCRIPTORS DEL PROCESO PID {pid_testigo_str}[/bold yellow]\n\n"
    lista_fds = datos_pid.get("lista", [])
    if lista_fds:
        for fd_item in lista_fds[:8]:
            texto += f"  [cyan]• FD {fd_item.get('fd', '?')}[/cyan] {fd_item.get('tipo', 'Desconocido')} -> {fd_item.get('destino', 'N/A')}\n"
    else:
        texto += "  [cyan]• Sin descriptores disponibles.[/cyan]"
    return texto


def construir_texto_threads(pid_testigo_str: str, datos_pid: dict) -> str:
    texto = f"[bold yellow]THREADS (LWPs) DEL PROCESO PID {pid_testigo_str}[/bold yellow]\n\n"
    lista_hilos = datos_pid.get("lista", [])
    if lista_hilos:
        for h in lista_hilos[:6]:
            texto += f"  [cyan]• TID {h.get('tid', '?')}[/cyan] {h.get('nombre', 'Desconocido')} | estado {h.get('estado', '?')} | cpu {h.get('cpu', 'N/A')} | ctx {h.get('ctx_voluntarios', '0')}/{h.get('ctx_involuntarios', '0')}\n"
    else:
        texto += "  [cyan]• No hay hilos adicionales.[/cyan]"
    return texto


def construir_texto_senales(pid_testigo_str: str, datos_pid: dict) -> str:
    texto = f"[bold yellow]SEÑALES DEL PROCESO PID {pid_testigo_str}[/bold yellow]\n\n"
    texto += f"  [cyan]• SigBlk:[/cyan] {', '.join(datos_pid.get('bloqueadas', [])) or 'Ninguna'}\n"
    texto += f"  [cyan]• SigIgn:[/cyan] {', '.join(datos_pid.get('ignoradas', [])) or 'Ninguna'}\n"
    texto += f"  [cyan]• SigCgt:[/cyan] {', '.join(datos_pid.get('capturadas', [])) or 'Ninguna'}\n"
    texto += f"  [cyan]• SigPnd:[/cyan] {', '.join(datos_pid.get('pendientes', [])) or 'Ninguna'}"
    return texto


def construir_texto_scheduling(pid_testigo_str: str, datos_pid: dict) -> str:
    texto = f"[bold yellow]SCHEDULING DEL PROCESO PID {pid_testigo_str}[/bold yellow]\n\n"
    texto += f"  [cyan]• Nice:[/cyan] {datos_pid.get('nice', 'N/A')}\n"
    texto += f"  [cyan]• Priority:[/cyan] {datos_pid.get('prioridad', 'N/A')}\n"
    texto += f"  [cyan]• Policy:[/cyan] {datos_pid.get('politica', 'N/A')}\n"
    texto += f"  [cyan]• Affinity:[/cyan] {datos_pid.get('cpus_allowed_list', 'N/A')}\n"
    texto += f"  [cyan]• Context switches:[/cyan] {datos_pid.get('ctx_voluntarios', '0')} voluntarios / {datos_pid.get('ctx_involuntarios', '0')} involuntarios"
    return texto


def construir_texto_sistema(stats_globales: dict, datos_resumen: dict) -> str:
    load_list = stats_globales.get("load_avg", ["0.00", "0.00", "0.00"])
    texto = "[bold yellow]STATS GLOBALES DEL SISTEMA[/bold yellow]\n\n"
    texto += f"  [cyan]• CPU global:[/cyan] {stats_globales.get('cpu_global', 'N/A')}\n"
    texto += f"  [cyan]• Load average:[/cyan] {' '.join(load_list)}\n"
    texto += f"  [cyan]• Memoria total/libre:[/cyan] {stats_globales.get('mem_total', 'N/A')} / {stats_globales.get('mem_libre', 'N/A')}\n"
    texto += f"  [cyan]• Memoria buffers/cached/swap:[/cyan] {stats_globales.get('mem_buffers', 'N/A')} / {stats_globales.get('mem_cached', 'N/A')} / {stats_globales.get('mem_swap', 'N/A')}\n"
    texto += f"  [cyan]• Procesos totales:[/cyan] {len(datos_resumen)}"
    return texto


def ejecutar_display(snapshot_compartido: dict, intervalos_compartidos: dict, shutdown_event: Event):
    """
    Bucle principal interactivo que procesa filtros, ordenamientos y las 7 vistas.
    """
    os.system("tput civis" if os.name == "posix" else "")
    
    # Estados locales para controlar los Keybindings Obligatorios
    vista_activa = "resumen"
    criterio_orden = "cpu"  # cpu, rss, pid
    mostrar_ayuda = False
    
    mapeo_teclas = {
        "1": "resumen", "r": "resumen", 
        "2": "memoria", "m": "memoria",
        "3": "fds",     "f": "fds",     
        "4": "threads", "t": "threads",
        "5": "senales", "s": "senales", 
        "6": "scheduling", "p": "scheduling",
        "7": "sistema",  "g": "sistema"
    }
    
    fd_stdin = sys.stdin.fileno()
    try:
        import tty
        import termios
        viejos_atributos = termios.tcgetattr(fd_stdin)
        tty.setcbreak(fd_stdin)
        
        with Live(auto_refresh=False, console=console) as live:
            while not shutdown_event.is_set():
                
                # --- PROCESAMIENTO DE TECLADO ---
                tecla = verificar_teclado().lower()
                
                if tecla == "q":
                    shutdown_event.set()
                    break
                elif tecla in ["h", "?", "h"]:
                    mostrar_ayuda = not mostrar_ayuda
                elif tecla in mapeo_teclas:
                    vista_activa = mapeo_teclas[tecla]
                    mostrar_ayuda = False
                elif tecla == "c":
                    criterio_orden = "rss" if criterio_orden == "cpu" else "pid" if criterio_orden == "rss" else "cpu"
                elif tecla == "+":
                    val_obj = intervalos_compartidos.get(vista_activa)
                    if val_obj: val_obj.value = max(0.5, val_obj.value - 0.5)
                elif tecla == "-":
                    val_obj = intervalos_compartidos.get(vista_activa)
                    if val_obj: val_obj.value = min(20.0, val_obj.value + 0.5)
                
                # --- OBTENER Y ORDENAR LISTA DE PROCESOS ---
                datos_resumen = snapshot_compartido.get("resumen", {}).get("procesos", {})
                lista_procesados = list(datos_resumen.values())
                
                if criterio_orden == "cpu":
                    lista_procesados.sort(key=lambda x: x["cpu_porc"], reverse=True)
                elif criterio_orden == "rss":
                    lista_procesados.sort(key=lambda x: int(x["rss"].replace("kB", "").replace("KB", "").replace(" ", "").strip() or 0), reverse=True)
                elif criterio_orden == "pid":
                    lista_procesados.sort(key=lambda x: x["pid"])

                # --- ESTRUCTURA DEL LAYOUT CORREGIDA PARA PYTHON 3.12 ---
                layout = Layout()
                layout.split_column(
                    Layout(name="header", size=int(3)),
                    Layout(name="main_panel", ratio=int(2)),
                    Layout(name="panel_detalle", ratio=int(1)),
                    Layout(name="footer", size=int(3))
                )
                
                # 1. RENDERIZAR ENCABEZADO GLOBAL
                stats_globales = snapshot_compartido.get("sistema", {})
                load_list = stats_globales.get("load_avg", ["0.00", "0.00", "0.00"])
                load_str = " ".join(load_list)
                layout["header"].update(Panel(
                    f"[bold green]MONITOR INTERACTIVO[/bold green] │ [cyan]Vista:[/cyan] [bold yellow]{vista_activa.upper()}[/bold yellow] │ [cyan]Orden:[/cyan] {criterio_orden.upper()} │ [cyan]Load Avg:[/cyan] {load_str}",
                    title=" Computacion II — Universidad de Mendoza ", title_align="left"
                ))

                            # 2. RENDERIZAR PANEL CENTRAL (Tabla de procesos o Ayuda)
                if mostrar_ayuda:
                    texto_ayuda = "[bold green]MENÚ DE AYUDA — KEYBINDINGS OBLIGATORIOS COMPLETO:[/bold green]\n\n"
                    texto_ayuda += "  [bold white]1 - 7 o r,m,f,t,s,p,g[/bold white] : Cambiar de vista activa en el panel de detalle\n"
                    texto_ayuda += "  [bold white]c[/bold white]                   : Toggle ordenamiento dinámico (CPU% / RSS / PID)\n"
                    texto_ayuda += "  [bold white]+ / -[/bold white]               : Ajustar intervalo de refresco de la vista activa\n"
                    texto_ayuda += "  [bold white]h[/bold white]                   : Cerrar este menú de ayuda\n"
                    texto_ayuda += "  [bold white]q[/bold white]                   : Salir limpiamente de toda la arquitectura"
                    layout["main_panel"].update(Panel(texto_ayuda, border_style="green"))
                else:
                    tabla = Table(expand=True, highlight=True)
                    tabla.add_column("PID", justify="right", style="cyan")
                    tabla.add_column("PPID", justify="right", style="magenta")
                    tabla.add_column("ESTADO", style="green")
                    tabla.add_column("CPU %", justify="right", style="yellow")
                    tabla.add_column("RAM (RSS)", justify="right", style="blue")
                    tabla.add_column("COMANDO", style="white")

                    if not lista_procesados:
                        tabla.add_row("-", "-", "Esperando", "0.0%", "0 KB", "sin datos")
                    else:
                        for p_info in lista_procesados[:6]:
                            tabla.add_row(
                                str(p_info["pid"]), str(p_info["ppid"]), p_info["estado"],
                                f"{p_info['cpu_porc']}%", p_info["rss"], p_info["comando"]
                            )
                    layout["main_panel"].update(tabla)
                
                # 3. RENDERIZAR PANEL INFERIOR DETALLADO SEGÚN LA VISTA ACTIVA
                intervalo_segundos = intervalos_compartidos[vista_activa].value if vista_activa in intervalos_compartidos else 0.0
                pid_testigo_str, datos_pid, proc_seccion, cajon_activo = obtener_datos_vista(snapshot_compartido, vista_activa, lista_procesados)

                if vista_activa == "sistema":
                    layout["panel_detalle"].update(Panel(construir_texto_sistema(stats_globales, datos_resumen), title=" VISTA 7: Sistema Global ", border_style="cyan"))
                elif pid_testigo_str and datos_pid:
                    if vista_activa == "resumen":
                        datos_p_res = datos_resumen.get(pid_testigo_str, {})
                        layout["panel_detalle"].update(Panel(construir_texto_resumen(pid_testigo_str, datos_p_res), title=" VISTA 1: Resumen General ", border_style="cyan"))
                    elif vista_activa == "memoria":
                        layout["panel_detalle"].update(Panel(construir_texto_memoria(pid_testigo_str, datos_pid), title=" VISTA 2: Segmentos de Memoria ", border_style="cyan"))
                    elif vista_activa == "fds":
                        layout["panel_detalle"].update(Panel(construir_texto_fds(pid_testigo_str, datos_pid), title=" VISTA 3: File Descriptors ", border_style="cyan"))
                    elif vista_activa == "threads":
                        layout["panel_detalle"].update(Panel(construir_texto_threads(pid_testigo_str, datos_pid), title=" VISTA 4: Threads Internos ", border_style="cyan"))
                    elif vista_activa == "senales":
                        layout["panel_detalle"].update(Panel(construir_texto_senales(pid_testigo_str, datos_pid), title=" VISTA 5: Señales de Entrada ", border_style="cyan"))
                    elif vista_activa == "scheduling":
                        layout["panel_detalle"].update(Panel(construir_texto_scheduling(pid_testigo_str, datos_pid), title=" VISTA 6: Configuración de Scheduling ", border_style="cyan"))
                else:
                    texto_espera = f"[bold yellow]Vista {vista_activa.upper()} cargando datos...[/bold yellow]\n\n"
                    texto_espera += "  [cyan]• El recolector está populando la información de esta vista.[/cyan]\n"
                    texto_espera += "  [cyan]• La tabla superior sigue mostrando los procesos detectados.[/cyan]\n"
                    texto_espera += "  [cyan]• Prueba con las teclas 1-7 para alternar entre vistas.[/cyan]"
                    layout["panel_detalle"].update(Panel(texto_espera, title=" Esperando datos de la vista ", border_style="yellow"))
                
                # 4. RENDERIZAR FOOTER INFORMATIVO
                layout["footer"].update(Panel(
                    f"[bold white][1-7 / r,m,f,t,s,p,g][/bold white] Alternar Vista │ [bold white][c][/bold white] Orden ({criterio_orden.upper()}) │ [bold white][+][-][/bold white] Refresco Activo ({intervalo_segundos}s) │ [bold white][h][/bold white] Ayuda │ [bold white][q][/bold white] Salir",
                    border_style="dim"
                ))
                
                live.update(layout, refresh=True)
                time.sleep(0.15)
                
    finally:
        try: termios.tcsetattr(fd_stdin, termios.TCSADRAIN, viejos_atributos)
        except Exception: pass
        os.system("tput cnorm" if os.name == "posix" else "")

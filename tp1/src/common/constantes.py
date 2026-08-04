"""
Constantes globales del monitor.
"""

# Nombres de las vistas

VISTA_RESUMEN = "resumen"
VISTA_MEMORIA = "memoria"
VISTA_FDS = "fds"
VISTA_THREADS = "threads"
VISTA_SENALES = "senales"
VISTA_SCHEDULING = "scheduling"
VISTA_SISTEMA = "sistema"

VISTAS = [
    VISTA_RESUMEN,
    VISTA_MEMORIA,
    VISTA_FDS,
    VISTA_THREADS,
    VISTA_SENALES,
    VISTA_SCHEDULING,
    VISTA_SISTEMA,
]

# Snapshot global

SECCIONES_SNAPSHOT = [
    "resumen",
    "memoria",
    "fds",
    "threads",
    "senales",
    "scheduling",
    "sistema",
]

# Ordenamientos posibles

ORDEN_CPU = "cpu"
ORDEN_MEMORIA = "rss"
ORDEN_PID = "pid"

# Estados Linux

ESTADOS_PROCESO = {
    "R": "Running",
    "S": "Sleeping",
    "D": "Disk Sleep",
    "T": "Stopped",
    "Z": "Zombie",
    "X": "Dead",
    "I": "Idle"
}
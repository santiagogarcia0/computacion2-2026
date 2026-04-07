#!/usr/bin/env python3
"""Información del sistema"""

import sys
import os
import platform

print("="*50)
print("INFO DEL SISTEMA")
print("="*50)

# Python
print(f"Python: {sys.version}")

# Sistema operativo
print(f"Sistema: {platform.system()} {platform.release()}")

# CPUs
print(f"CPUs disponibles: {os.cpu_count()}")

# Memoria (intento)
try:
    if hasattr(os, "sysconf"):
        mem_bytes = os.sysconf('SC_PAGE_SIZE') * os.sysconf('SC_PHYS_PAGES')
        mem_gb = mem_bytes / (1024**3)
        print(f"Memoria total aprox: {mem_gb:.2f} GB")
    else:
        print("Memoria: no disponible")
except:
    print("Memoria: no se pudo obtener")

# Variables de entorno PYTHON
print("\nVariables de entorno (PYTHON*):")
for k, v in os.environ.items():
    if k.startswith("PYTHON"):
        print(f"{k}={v}")

print("="*50)
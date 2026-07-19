#!/usr/bin/env python3
"""Suma paralela usando mmap anónimo y fork."""

import mmap
import os
import struct

NUM_HIJOS = 4
TAMAÑO_POR_HIJO = 64
TAMAÑO_TOTAL = NUM_HIJOS * TAMAÑO_POR_HIJO

mm = mmap.mmap(-1, TAMAÑO_TOTAL)

hijos = []

for i in range(NUM_HIJOS):
    pid = os.fork()

    if pid == 0:
        # Región del hijo
        offset = i * TAMAÑO_POR_HIJO

        # Rangos:
        # Hijo 0 -> 1-25
        # Hijo 1 -> 26-50
        # Hijo 2 -> 51-75
        # Hijo 3 -> 76-100
        inicio = i * 25 + 1
        fin = (i + 1) * 25

        suma = sum(range(inicio, fin + 1))

        # Guardar datos
        struct.pack_into('i', mm, offset, i)              # id hijo
        struct.pack_into('i', mm, offset + 4, os.getpid()) # pid
        struct.pack_into('i', mm, offset + 8, suma)        # suma parcial

        os._exit(0)

    else:
        hijos.append(pid)

# Padre espera a todos los hijos
for pid in hijos:
    os.waitpid(pid, 0)

print("=== Resultados parciales ===")

suma_total = 0

for i in range(NUM_HIJOS):
    offset = i * TAMAÑO_POR_HIJO

    hijo_id = struct.unpack_from('i', mm, offset)[0]
    hijo_pid = struct.unpack_from('i', mm, offset + 4)[0]
    suma_parcial = struct.unpack_from('i', mm, offset + 8)[0]

    suma_total += suma_parcial

    print(
        f"Hijo {hijo_id} (PID {hijo_pid}) -> "
        f"suma parcial = {suma_parcial}"
    )

print(f"\nSuma total = {suma_total}")

mm.close()
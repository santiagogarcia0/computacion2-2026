#!/usr/bin/env python3

import mmap
import os
import struct

NUM_HIJOS = 4
TAMAÑO_POR_HIJO = 32
TAMAÑO_TOTAL = NUM_HIJOS * TAMAÑO_POR_HIJO

mm = mmap.mmap(-1, TAMAÑO_TOTAL)

hijos = []

for i in range(NUM_HIJOS):

    pid = os.fork()

    if pid == 0:

        # ===== HIJO =====

        inicio = i * 25 + 1
        fin = (i + 1) * 25

        suma = sum(range(inicio, fin + 1))

        offset = i * TAMAÑO_POR_HIJO

        # Guardar datos
        struct.pack_into('i', mm, offset, i)
        struct.pack_into('i', mm, offset + 4, inicio)
        struct.pack_into('i', mm, offset + 8, fin)
        struct.pack_into('i', mm, offset + 12, suma)

        print(f"[HIJO {i}] Suma {inicio}-{fin} = {suma}")

        os._exit(0)

    else:
        hijos.append(pid)

# ===== PADRE =====

for pid in hijos:
    os.waitpid(pid, 0)

print("\n=== Resultados parciales ===")

total = 0

for i in range(NUM_HIJOS):

    offset = i * TAMAÑO_POR_HIJO

    hijo_id = struct.unpack_from('i', mm, offset)[0]
    inicio = struct.unpack_from('i', mm, offset + 4)[0]
    fin = struct.unpack_from('i', mm, offset + 8)[0]
    suma = struct.unpack_from('i', mm, offset + 12)[0]

    total += suma

    print(f"Hijo {hijo_id}: suma {inicio}-{fin} = {suma}")

print(f"\nSUMA TOTAL = {total}")

mm.close()
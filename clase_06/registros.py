#!/usr/bin/env python3

import mmap
import struct
import os

ARCHIVO = "/tmp/registros.bin"

FORMATO = 'i f 20s'
TAM_REGISTRO = struct.calcsize(FORMATO)

NUM_REGISTROS = 5
TAMAÑO_TOTAL = TAM_REGISTRO * NUM_REGISTROS

# Crear archivo vacío
with open(ARCHIVO, "wb") as f:
    f.write(b'\x00' * TAMAÑO_TOTAL)

# Datos de ejemplo
datos = [
    (1, 8.5, "Juan"),
    (2, 7.2, "Maria"),
    (3, 9.1, "Pedro"),
    (4, 6.8, "Lucia"),
    (5, 10.0, "Ana")
]

with open(ARCHIVO, "r+b") as f:
    mm = mmap.mmap(f.fileno(), TAMAÑO_TOTAL)

    print("=== Escribiendo registros ===")

    # Escribir registros
    for i, (id_, nota, nombre) in enumerate(datos):

        offset = i * TAM_REGISTRO

        nombre_bytes = nombre.encode().ljust(20, b'\x00')

        struct.pack_into(
            FORMATO,
            mm,
            offset,
            id_,
            nota,
            nombre_bytes
        )

        print(f"Registro {i}: {id_}, {nota}, {nombre}")

    print("\n=== Leyendo registros ===")

    # Leer registros
    for i in range(NUM_REGISTROS):

        offset = i * TAM_REGISTRO

        id_, nota, nombre = struct.unpack_from(
            FORMATO,
            mm,
            offset
        )

        nombre = nombre.decode().rstrip('\x00')

        print(f"Registro {i}:")
        print(f"  ID: {id_}")
        print(f"  Nota: {nota}")
        print(f"  Nombre: {nombre}")

    mm.close()

os.unlink(ARCHIVO)
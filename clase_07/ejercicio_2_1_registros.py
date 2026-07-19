#!/usr/bin/env python3
"""Almacenar registros usando mmap y struct."""

import mmap
import struct
import os

ARCHIVO = "/tmp/registros.bin"

# entero + float + 20 caracteres
FORMATO = "i f 20s"
TAM_REGISTRO = struct.calcsize(FORMATO)
NUM_REGISTROS = 5

# Crear archivo con tamaño fijo
with open(ARCHIVO, "wb") as f:
    f.write(b"\x00" * (TAM_REGISTRO * NUM_REGISTROS))

with open(ARCHIVO, "r+b") as f:
    mm = mmap.mmap(f.fileno(), 0)

    # Escribir registros
    print("=== Escribiendo registros ===")

    datos = [
        (1, 8.5, "Juan"),
        (2, 9.0, "Maria"),
        (3, 7.8, "Pedro"),
        (4, 10.0, "Ana"),
        (5, 6.9, "Lucas")
    ]

    for i, (id_, nota, nombre) in enumerate(datos):
        offset = i * TAM_REGISTRO
        struct.pack_into(
            FORMATO,
            mm,
            offset,
            id_,
            nota,
            nombre.encode()
        )

        print(f"ID={id_}, Nota={nota}, Nombre={nombre}")

    # Leer registros
    print("\n=== Leyendo registros ===")

    for i in range(NUM_REGISTROS):
        offset = i * TAM_REGISTRO

        id_, nota, nombre = struct.unpack_from(
            FORMATO,
            mm,
            offset
        )

        nombre = nombre.decode().rstrip('\x00')

        print(f"ID={id_}, Nota={nota}, Nombre={nombre}")

    mm.close()

os.unlink(ARCHIVO)
#!/usr/bin/env python3
import mmap

with open("/tmp/mmap_test.txt", "r+b") as f:
    mm = mmap.mmap(f.fileno(), 0)

    palabra = b"mmap"
    nueva = b"MMAP"

    pos = mm.find(palabra)

    if pos != -1:
        print(f"Encontrado en posicion {pos}")

        mm.seek(pos)
        mm.write(nueva)

        print("Reemplazo realizado")
    else:
        print("Palabra no encontrada")

    mm.close()
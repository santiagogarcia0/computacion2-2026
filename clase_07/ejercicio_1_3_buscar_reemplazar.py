#!/usr/bin/env python3
import mmap

# Crear archivo con 5 líneas
with open("/tmp/ejercicio_mmap.txt", "wb") as f:
    f.write(b"Python es divertido\n")
    f.write(b"Me gusta programar\n")
    f.write(b"Python sirve para automatizar\n")
    f.write(b"Computacion II\n")
    f.write(b"Fin del archivo\n")

# Mapear y modificar
with open("/tmp/ejercicio_mmap.txt", "r+b") as f:
    mm = mmap.mmap(f.fileno(), 0)

    palabra_buscar = b"Python"
    palabra_nueva = b"PYTHON"   # mismo largo (6 caracteres)

    pos = mm.find(palabra_buscar)

    if pos != -1:
        print(f"Palabra encontrada en la posicion {pos}")
        mm.seek(pos)
        mm.write(palabra_nueva)
        print("Reemplazo realizado")
    else:
        print("Palabra no encontrada")

    mm.close()
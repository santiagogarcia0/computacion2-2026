#!/usr/bin/env python3
"""Mini-shell con redirección."""
import os
import sys

def parsear_linea(linea):
    partes = linea.split()
    if not partes:
        return None, [], None, None

    comando = partes[0]
    args = []
    archivo_salida = None
    archivo_entrada = None

    i = 1
    while i < len(partes):
        if partes[i] == ">":
            if i + 1 < len(partes):
                archivo_salida = partes[i + 1]
            i += 2
        elif partes[i] == "<":
            if i + 1 < len(partes):
                archivo_entrada = partes[i + 1]
            i += 2
        else:
            args.append(partes[i])
            i += 1

    return comando, args, archivo_salida, archivo_entrada


def ejecutar(comando, args, archivo_salida=None, archivo_entrada=None):
    pid = os.fork()

    if pid == 0:
        # 🔴 HIJO

        # Redirección de salida (>)
        if archivo_salida:
            fd = os.open(archivo_salida,
                         os.O_CREAT | os.O_WRONLY | os.O_TRUNC,
                         0o644)
            os.dup2(fd, 1)
            os.close(fd)

        # Redirección de entrada (<)
        if archivo_entrada:
            try:
                fd = os.open(archivo_entrada, os.O_RDONLY)
                os.dup2(fd, 0)
                os.close(fd)
            except OSError as e:
                print(f"Error abriendo {archivo_entrada}: {e}", file=sys.stderr)
                os._exit(1)

        # Ejecutar comando
        try:
            os.execvp(comando, [comando] + args)
        except OSError as e:
            print(f"minish: {comando}: {e}", file=sys.stderr)
            os._exit(127)

    else:
        # 🔵 PADRE
        _, status = os.wait()
        return os.WEXITSTATUS(status)


def main():
    while True:
        try:
            linea = input("minish$ ")
        except EOFError:
            print("\nChau!")
            break

        linea = linea.strip()
        if not linea:
            continue

        if linea == "exit":
            break

        comando, args, salida, entrada = parsear_linea(linea)

        if comando:
            ejecutar(comando, args, salida, entrada)


if __name__ == "__main__":
    main()
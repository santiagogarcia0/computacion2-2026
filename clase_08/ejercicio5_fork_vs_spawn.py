#!/usr/bin/env python3

from multiprocessing import Process, set_start_method
import time
import sys


def tarea():
    pass


if __name__ == "__main__":

    # Elegir el método desde la línea de comandos
    # Ejemplo:
    # python ejercicio5_fork_vs_spawn.py fork
    # python ejercicio5_fork_vs_spawn.py spawn

    metodo = sys.argv[1] if len(sys.argv) > 1 else "spawn"

    set_start_method(metodo)

    procesos = []

    inicio = time.perf_counter()

    for _ in range(100):
        p = Process(target=tarea)
        procesos.append(p)
        p.start()

    for p in procesos:
        p.join()

    fin = time.perf_counter()

    print(f"Método: {metodo}")
    print(f"Tiempo para crear y ejecutar 100 procesos: {fin - inicio:.4f} segundos")
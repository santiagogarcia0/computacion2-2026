#!/usr/bin/env python3
"""Comparación secuencial vs paralelo."""

from multiprocessing import Pool
import time
import math


def cpu_task(n):
    """Tarea CPU-intensive."""
    return sum(math.sqrt(i) for i in range(n))


N = 500_000
TAREAS = 8

if __name__ == "__main__":

    # Ejecución secuencial
    inicio = time.perf_counter()
    resultados = [cpu_task(N) for _ in range(TAREAS)]
    t_seq = time.perf_counter() - inicio

    print(f"Secuencial: {t_seq:.2f}s\n")

    print("Workers | Tiempo (s) | Speedup")
    print("-" * 32)

    for workers in [1, 2, 4, 8]:
        inicio = time.perf_counter()

        with Pool(workers) as pool:
            resultados = pool.map(cpu_task, [N] * TAREAS)

        t_par = time.perf_counter() - inicio
        speedup = t_seq / t_par

        print(f"{workers:^7} | {t_par:^10.2f} | {speedup:^7.2f}x")
#!/usr/bin/env python3

from multiprocessing import Process
import time
import random
import os


def worker(numero):
    duracion = random.uniform(0.5, 2)
    print(f"Worker {numero} (PID={os.getpid()}) trabajando durante {duracion:.2f} s")
    time.sleep(duracion)
    print(f"Worker {numero} terminó")


if __name__ == "__main__":
    procesos = []

    inicio = time.time()

    # Crear e iniciar los 5 workers
    for i in range(5):
        p = Process(target=worker, args=(i,))
        procesos.append(p)
        p.start()

    # Esperar a que todos terminen
    for p in procesos:
        p.join()

    fin = time.time()

    print(f"\nTodos los workers terminaron.")
    print(f"Tiempo total: {fin - inicio:.2f} segundos")
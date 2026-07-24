#!/usr/bin/env python3
"""Usar Manager para compartir estructuras complejas."""

from multiprocessing import Process, Manager
import time
import random


def worker(shared_dict, shared_list, worker_id):
    # Simular trabajo
    duracion = random.uniform(0.2, 1.0)
    time.sleep(duracion)

    # Guardar información en el diccionario compartido
    shared_dict[f"worker_{worker_id}"] = {
        "status": "done",
        "result": worker_id ** 2,
        "duracion": round(duracion, 2)
    }

    # Agregar mensaje a la lista compartida
    shared_list.append(
        f"Worker {worker_id} completó en {duracion:.2f}s"
    )


if __name__ == "__main__":

    with Manager() as manager:

        d = manager.dict()
        l = manager.list()

        procesos = [
            Process(target=worker, args=(d, l, i))
            for i in range(5)
        ]

        for p in procesos:
            p.start()

        for p in procesos:
            p.join()

        print("Diccionario compartido:")

        for k, v in d.items():
            print(f"  {k}: {v}")

        print("\nLista compartida (orden de finalización):")

        for item in l:
            print(f"  {item}")
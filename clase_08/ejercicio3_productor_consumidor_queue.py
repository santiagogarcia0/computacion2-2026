#!/usr/bin/env python3

from multiprocessing import Process, Queue
import time
import random


def productor(queue):
    for i in range(10):
        print(f"Productor: generó el item {i}")
        queue.put(i)
        time.sleep(random.uniform(0.2, 0.6))

    # Señal de fin
    queue.put(None)


def consumidor(queue):
    while True:
        item = queue.get()

        if item is None:
            break

        print(f"Consumidor: procesando el item {item}")
        time.sleep(random.uniform(0.3, 0.7))

    print("Consumidor: terminó de procesar todos los items.")


if __name__ == "__main__":
    cola = Queue()

    p_productor = Process(target=productor, args=(cola,))
    p_consumidor = Process(target=consumidor, args=(cola,))

    p_productor.start()
    p_consumidor.start()

    p_productor.join()
    p_consumidor.join()

    print("Programa finalizado.")
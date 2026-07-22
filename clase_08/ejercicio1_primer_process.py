#!/usr/bin/env python3

from multiprocessing import Process
import os


def hijo():
    print(f"Soy el hijo: PID={os.getpid()}, padre={os.getppid()}")


if __name__ == "__main__":
    p = Process(target=hijo)

    p.start()  # Crea e inicia el proceso hijo

    print(f"Soy el padre: PID={os.getpid()}, hijo={p.pid}")

    p.join()   # Espera a que termine el hijo

    print("Programa terminado")
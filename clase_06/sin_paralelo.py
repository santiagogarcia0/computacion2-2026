#!/usr/bin/env python3

from multiprocessing import Process, Array, Value
import math

TAMAÑO = 100
NUM_PROCESOS = 4

# Array compartido de doubles
resultado = Array('d', TAMAÑO)

# Suma compartida (bonus)
suma_total = Value('d', 0.0)

def calcular(resultado, suma_total, inicio, fin):

    suma_local = 0.0

    for i in range(inicio, fin):

        valor = math.sin(i * 0.01)

        resultado[i] = valor

        suma_local += valor

    # BONUS:
    # Esto puede tener race condition
    with suma_total.get_lock():
        suma_total.value += suma_local

    print(f"Proceso {inicio}-{fin} terminado")


chunk = TAMAÑO // NUM_PROCESOS

procesos = []

for i in range(NUM_PROCESOS):

    ini = i * chunk

    fin = (
        (i + 1) * chunk
        if i < NUM_PROCESOS - 1
        else TAMAÑO
    )

    p = Process(
        target=calcular,
        args=(resultado, suma_total, ini, fin)
    )

    p.start()

    procesos.append(p)

for p in procesos:
    p.join()

print("\n=== Primeros 20 resultados ===")

for i in range(20):
    print(f"{i}: {resultado[i]}")

print(f"\nSuma total: {suma_total.value}")
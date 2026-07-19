#!/usr/bin/env python3
"""Array compartido con funciones seno."""

from multiprocessing import Process, Array, Value
import math

def calcular_seno(datos, suma_total, inicio, fin):
    """Calcula sin(i * 0.01) para una porción del array."""
    
    suma_local = 0.0

    for i in range(inicio, fin):
        valor = math.sin(i * 0.01)
        datos[i] = valor
        suma_local += valor

    # BONUS: acumular en valor compartido
    # (sin lock explícito para observar posibles race conditions)
    suma_total.value += suma_local


TAMAÑO = 100
NUM_PROCESOS = 4

datos = Array('d', TAMAÑO)
suma_total = Value('d', 0.0)

chunk = TAMAÑO // NUM_PROCESOS

procesos = []

for i in range(NUM_PROCESOS):
    inicio = i * chunk
    fin = (i + 1) * chunk if i < NUM_PROCESOS - 1 else TAMAÑO

    p = Process(
        target=calcular_seno,
        args=(datos, suma_total, inicio, fin)
    )

    p.start()
    procesos.append(p)

for p in procesos:
    p.join()

print("=== Primeros 20 resultados ===")

for i in range(20):
    print(f"datos[{i}] = {datos[i]:.6f}")

print(f"\nSuma total compartida = {suma_total.value:.6f}")
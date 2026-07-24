#!/usr/bin/env python3
"""
Procesador de imágenes paralelo.
Simula procesamiento de imágenes usando matrices.
"""

from multiprocessing import Pool
import time
import random


def crear_imagen(size):
    """Genera una imagen aleatoria."""
    return [
        [random.randint(0, 255) for _ in range(size)]
        for _ in range(size)
    ]


def aplicar_filtro(imagen):
    """
    Filtro blur 3x3.
    Cada píxel se reemplaza por el promedio
    de sus vecinos.
    """
    size = len(imagen)

    resultado = [
        [0] * size
        for _ in range(size)
    ]

    for i in range(1, size - 1):
        for j in range(1, size - 1):

            suma = 0

            for di in (-1, 0, 1):
                for dj in (-1, 0, 1):
                    suma += imagen[i + di][j + dj]

            resultado[i][j] = suma // 9

    return resultado


def procesar_imagen(args):
    """
    Procesa una imagen completa y devuelve:
    índice, duración y checksum.
    """
    idx, imagen = args

    inicio = time.perf_counter()

    resultado = aplicar_filtro(imagen)

    duracion = time.perf_counter() - inicio

    checksum = sum(sum(fila) for fila in resultado)

    return idx, duracion, checksum


if __name__ == "__main__":

    NUM_IMAGENES = 8
    SIZE = 100

    print(f"Creando {NUM_IMAGENES} imágenes de {SIZE}x{SIZE}...\n")

    imagenes = [
        (i, crear_imagen(SIZE))
        for i in range(NUM_IMAGENES)
    ]

    # -------------------------
    # Procesamiento secuencial
    # -------------------------

    print("Procesamiento secuencial:")

    inicio = time.perf_counter()

    resultados_seq = [
        procesar_imagen(img)
        for img in imagenes
    ]

    tiempo_secuencial = time.perf_counter() - inicio

    print(f"Tiempo total: {tiempo_secuencial:.3f}s")

    # -------------------------
    # Procesamiento paralelo
    # -------------------------

    print("\nProcesamiento paralelo (Pool 4 workers):")

    inicio = time.perf_counter()

    with Pool(4) as pool:
        resultados_par = pool.map(
            procesar_imagen,
            imagenes
        )

    tiempo_paralelo = time.perf_counter() - inicio

    for idx, duracion, checksum in resultados_par:
        print(
            f"Imagen {idx}: "
            f"{duracion:.3f}s "
            f"(checksum={checksum})"
        )

    speedup = tiempo_secuencial / tiempo_paralelo

    print(f"\nTiempo paralelo: {tiempo_paralelo:.3f}s")
    print(f"Speedup: {speedup:.2f}x")
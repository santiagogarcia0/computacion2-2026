#!/usr/bin/env python3

import threading
import time

def imprimir_numeros(nombre):
    for i in range(1, 6):
        print(f"[{nombre}] número: {i}")
        time.sleep(0.2)

# Crear los hilos
hilos = [
    threading.Thread(target=imprimir_numeros, args=(f"Hilo-{i}",))
    for i in range(1, 4)
]

# Iniciar los hilos
for hilo in hilos:
    hilo.start()

# Esperar que terminen
for hilo in hilos:
    hilo.join()

print("Listo")
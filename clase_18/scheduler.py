from collections import deque

def tarea(nombre, pasos):
    for i in range(1, pasos + 1):
        print(f"[{nombre}] Paso {i}")
        yield  # Cede el control al scheduler

def scheduler(tareas):
    pendientes = deque(tareas)
    contador_next = 0
    
    while pendientes:
        tarea_actual = pendientes.popleft()  # Sacar la primera de la cola
        try:
            contador_next += 1
            next(tarea_actual)              # Reanudar la tarea
            pendientes.append(tarea_actual) # Si no terminó, vuelve a la cola
        except StopIteration:
            # La tarea terminó (ya no tiene más pasos/yields)
            print(f"--- Tarea finalizada ---")
            
    print(f"\n[Scheduler] El ciclo terminó. Se llamó a next() {contador_next} veces en total.")

import time

def tarea_egoista(nombre):
    print(f' [{nombre}] me pongo a calcular')
    time.sleep(3) # Bloquea TODO el hilo de ejecución
    print(f' [{nombre}] listo')
    yield

# Probamos metiendo la egoísta en medio
scheduler([tarea("Tarea A", 2), tarea_egoista("Egoísta"), tarea("Tarea C", 2)])

# --- Ejecución ---
# Creamos tres tareas con distinta cantidad de pasos
t1 = tarea("Tarea A", 3)
t2 = tarea("Tarea B", 1)
t3 = tarea("Tarea C", 2)

scheduler([t1, t2, t3])

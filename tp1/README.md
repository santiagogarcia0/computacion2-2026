# Monitor de procesos concurrente con vistas de /proc

Alumno: Santiago García

## 1. Descripción general

Este proyecto implementa un monitor de procesos en tiempo real para Linux que extrae información directamente del sistema de archivos virtual `/proc`. La herramienta corre como una arquitectura multiproceso y muestra una interfaz de texto interactiva (TUI) con 7 vistas alternables:

- Resumen
- Memoria
- File descriptors
- Threads (LWPs)
- Señales
- Scheduling
- Sistema global

La idea principal es mostrar, para un conjunto de procesos activos, los datos pedidos en la consigna del TP sin depender de librerías externas como `psutil`. Toda la telemetría se obtiene leyendo archivos como `/proc/<pid>/status`, `/proc/<pid>/stat`, `/proc/<pid>/maps`, `/proc/<pid>/fd`, `/proc/<pid>/task`, `/proc/stat`, `/proc/loadavg` y `/proc/meminfo`.

### Qué hace el monitor

- Detecta procesos vivos y los ordena según CPU, RSS o PID.
- Muestra un panel superior con un resumen de procesos.
- Muestra un panel inferior con datos detallados según la vista activa.
- Permite alternar vistas con las teclas `1`-`7` o `r/m/f/t/s/p/g`.
- Permite cambiar el ordenamiento con `c` y ajustar el refresco con `+` y `-`.
- Permite salir limpiamente con `q`.

### Cómo se usa

1. Entrar al directorio del proyecto:

```bash
cd tp1/src
```

2. Ejecutar el monitor:

```bash
python3 main.py
```

3. Usar los keybindings:

- `1`-`7` o `r/m/f/t/s/p/g`: cambiar vista
- `c`: alternar ordenamiento entre CPU, RSS y PID
- `+` / `-`: ajustar el intervalo de refresco de la vista activa
- `h` / `?`: mostrar ayuda
- `q`: salir

> Requiere un entorno Linux o WSL con acceso a `/proc`.

---

## 2. Diagrama de arquitectura

```text
+---------------------------+
|      Proceso Padre        |
|  - TUI / Display          |
|  - captura teclado       |
|  - snapshot compartido    |
+-------------+-------------+
              |
              | manager.dict / Value / Event
              |
+-------------+-------------+
|      Recolector          |
|  - escanea /proc         |
|  - distribuye PIDs       |
+-------------+-------------+
              |
      +-------+-------+-------+-------+-------+-------+
      |       |       |       |       |       |       |
+-----v-+ +--v---+ +--v---+ +--v---+ +--v---+ +--v---+
|Resumen| |Memoria| |FDs   | |Threads| |Señales| |Scheduling|
|Analiz.| |Analiz.| |Analiz.| |Analiz.| |Analiz.| |Analiz.|
+---^---+ +---^---+ +---^---+ +---^---+ +---^---+ +---^---+
    |         |         |         |         |         |
    +---------+---------+---------+---------+---------+
                      |
                 +----v----+
                 |Sistema  |
                 |Analizador|
                 +---------+
```

### Comunicación entre componentes

- El recolector central recibe los PIDs activos de `/proc`.
- Envía esos PIDs a colas separadas para cada analizador.
- Cada analizador procesa la dimensión correspondiente y actualiza el snapshot global compartido.
- El proceso padre renderiza la TUI usando la información más reciente del snapshot.

---

## 3. Decisiones de diseño argumentadas

### ¿Por qué elegí este mecanismo de IPC y no otro?

Se eligió una combinación de `multiprocessing.Queue` y `multiprocessing.Manager` porque el problema tiene dos necesidades distintas:

1. Distribuir PIDs desde un recolector hacia múltiples analizadores de forma segura.
2. Compartir estructuras complejas como diccionarios anidados con datos por proceso.

Las colas permiten que cada analizador reciba los PIDs de forma ordenada y sin interferencias. El `Manager` permite alojar un `dict` mutable con datos de distintos tipos y claves dinámicas (por ejemplo, los PIDs como strings). Esto encaja muy bien con la naturaleza del monitor.

### ¿Por qué `Manager` y no `Value`/`Array` para algunas cosas?

`Value` y `Array` son apropiados para datos numéricos o fijos, pero no para estructuras complejas como el snapshot general del monitor. El snapshot necesita guardar por ejemplo:

- datos resumidos por proceso,
- listas de FDs,
- listas de threads,
- máscaras de señales,
- y métricas globales del sistema.

Por eso se eligió un `manager.dict()` para ese componente y `Value` solo para los intervalos de refresco.

### ¿Cómo se manejaron las race conditions?

Cada analizador escribe en una sección distinta del snapshot global. Esto evita que dos procesos compitan por la misma clave de memoria compartida. Además, la lógica de drenado de colas se implementó de forma robusta para evitar inconsistencias al procesar los PIDs entrantes. El diseño busca que cada sección del snapshot sea escrita por un único productor.

### ¿Por qué estos intervalos por defecto?

Los intervalos se eligieron considerando el costo de las operaciones sobre `/proc`:

- Resumen: refresco relativamente frecuente porque lee información simple y rápida.
- Memoria: un poco más costoso por el análisis de `/proc/<pid>/maps`.
- FDs: más costoso porque requiere listar y resolver enlaces simbólicos.
- Threads y señales: más costosos que el resumen, pero menos que FDs.
- Sistema global: se actualiza con frecuencia porque la vista global depende de métricas de kernel.

El objetivo fue equilibrar estabilidad visual y costo computacional.

---

## 4. Conceptos del curso aplicados

El proyecto está fuertemente conectado con varios conceptos vistos en la materia:

1. **Paralelismo real y procesos**
   - Se usan `multiprocessing.Process` para tener procesos hijos reales, evitando las limitaciones del GIL.
   - Esto se relaciona directamente con la idea de que los procesos tienen su propio espacio de memoria y pueden correr en paralelo.

2. **Fork / exec / wait y estados de procesos**
   - La vista de sistema usa el estado del proceso leído desde `/proc/<pid>/stat`.
   - Este concepto está vinculado con el análisis de procesos vivos, zombies y estados del ciclo de vida.

3. **Planificador y cambios de contexto**
   - La vista de threads y scheduling usa información de `/proc/<pid>/task/...` y del estado del planificador.
   - Esto conecta con la clase sobre scheduler, context switches y prioridades.

4. **Señales y manejo asíncrono**
   - El monitor usa señales del sistema para controlar el ciclo de vida de la arquitectura.
   - La lógica de shutdown se organiza para que el programa finalice de manera ordenada.

5. **Sistemas de archivos virtuales y `/proc`**
   - Toda la recolección de datos se basa en el uso de procfs como fuente de observación del kernel.
   - Esto es central para el trabajo práctico porque permite inspeccionar procesos sin depender de herramientas externas.

---

## 5. Limitaciones conocidas

El programa funciona bien para el objetivo del TP, pero tiene algunas limitaciones:

- La lectura de FDs puede estar restringida por permisos para procesos de otros usuarios.
- La TUI está pensada para entornos Linux/WSL; no está orientada a Windows nativo.
- La captura de teclado en terminal raw es suficiente para las teclas requeridas por la consigna, pero no implementa completamente la navegación con flechas como en `htop`.
- El monitor depende del estado actual del kernel y de la disponibilidad de `/proc`; si un proceso termina durante la lectura, algunas entradas pueden quedar incompletas.
- El detalle mostrado en cada vista depende de la sincronización del snapshot; si los datos aún no llegaron, la interfaz puede mostrar un estado de espera temporal.

---

## 6. Cómo correr y testear

### Requisitos

- Python 3.10 o superior
- Linux o WSL
- Paquete `rich`

Si falta `rich`, instalarlo con:

```bash
pip install rich
```

### Ejecución principal

```bash
cd tp1/src
python3 main.py
```

### Verificación de sintaxis

```bash
cd tp1/src
python3 -m compileall .
```

### Prueba de la salida del display

```bash
cd tp1
python3 -m unittest discover -s tests -p "test_display_content.py"
```

### Ejemplo de prueba rápida

```bash
cd tp1/src
timeout 8s python3 main.py
```

Este último comando permite verificar que el monitor arranca y renderiza la TUI durante unos segundos sin quedar colgado.

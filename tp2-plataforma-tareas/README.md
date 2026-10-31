TP2 - Plataforma de Tareas Distribuidas
Santiago García
Computación II

Este trabajo práctico consiste en una plataforma de tareas distribuidas implementada en Python utilizando FastAPI y asyncio.

La aplicación permite recibir tareas mediante HTTP, encolarlas, ejecutarlas de forma concurrente utilizando un pool de workers y consultar su estado o resultado en cualquier momento.

El objetivo principal fue poner en práctica conceptos vistos durante el cursado como corrutinas, event loop, concurrencia, productor-consumidor, colas asíncronas y diferencias entre tareas I/O-bound y CPU-bound.

- TECNOLOGIAS UTILIZADAS
Python 3.12
FastAPI
asyncio
aiohttp
Docker
Docker Compose
Uvicorn

- ARQUITECTURA

Cliente HTTP
        |
        v
+-------------------+
| FastAPI           |
+-------------------+
        |
        v
+-------------------+
| Task Manager      |
+-------------------+
        |
        v
+-------------------+
| asyncio.Queue     |
+-------------------+
        |
        v
+-------------------+
| Pool Workers      |
| (4 workers)       |
+-------------------+
        |
        |
   +---------------+
   |               |
   v               v
Tareas I/O     Tareas CPU
(aiohttp)      (to_thread)
   |
   v
Resultado almacenado
en memoria

- FLUJO DE UNA TAREA
1) El cliente realiza un POST /tareas.
2) La API crea un ID único.
3) La tarea se almacena en memoria.
4) El ID de la tarea se agrega a una asyncio.Queue.
5) Un worker toma la tarea de la cola.
6) La tarea cambia su estado a ejecutando.
7) Se ejecuta según su tipo.
8) Se almacena el resultado.
9) El estado pasa a completada, fallida o cancelada.

Tipos de tarea implementados

- esperar
Simula una operación I/O utilizando:
await asyncio.sleep(...)

Se utilizó para probar:
* concurrencia
* cancelación
* timeouts

- descargar
Recibe una lista de URLs y las descarga concurrentemente utilizando:
* aiohttp y asyncio.gather()

Devuelve:
URL
código HTTP
tamaño descargado
tiempo empleado

- hashear
Tarea CPU-bound que aplica SHA-256 múltiples veces.
Se ejecuta mediante asyncio.to_thread() para evitar bloquear el event loop.

API
- Crear tarea:
POST /tareas

Ejemplo:
{
"type": "esperar",
"payload": {
"seconds": 10
},
"timeout": 30
}

* Listar tareas: GET /tareas

* Consultar tarea: GET /tareas/{id}

* Cancelar tarea: DELETE /tareas/{id}

* Estadísticas: GET /estadisticas
 
EJEMPLOS DE USO CON CURL
Crear tarea
curl -X POST "http://127.0.0.1:8000/tareas" \
  -H "Content-Type: application/json" \
  -d '{
    "type":"esperar",
    "payload":{
      "seconds":10
    },
    "timeout":30
}'

* Obtener estadísticas: curl http://127.0.0.1:8000/estadisticas
 
* Consultar tarea: curl http://127.0.0.1:8000/tareas/ID

Decisiones de diseño
¿Por qué asyncio.Queue y no queue.Queue?
Elegí asyncio.Queue porque todo el sistema está basado en corrutinas.
Los workers consumen tareas utilizando:
await queue.get() sin bloquear el event loop.
Si hubiera utilizado queue.Queue, los workers podrían bloquear el hilo principal mientras esperan tareas.

¿Cómo evité que una tarea CPU-bound congele la API?
Las tareas de hash se ejecutan mediante: asyncio.to_thread()
Esto mueve el cálculo a un thread separado.
De esta forma el event loop queda libre para seguir atendiendo peticiones HTTP.

¿Cómo implementé la cancelación?
Cada tarea en ejecución queda registrada dentro del TaskManager.
Cuando llega:
HTTP
DELETE /tareas/{id}

se busca la corrutina asociada y se ejecuta:
task.cancel()
Luego la tarea pasa al estado cancelada

¿Qué pasa si un worker lanza una excepción?
Cada worker tiene manejo de excepciones mediante:
try:
...
except:
...

Si ocurre un error:
- la tarea pasa a estado fallida
- se almacena el mensaje de error
- el worker sigue funcionando normalmente

De esta manera una tarea defectuosa no rompe todo el sistema.

MEDICIONES
- Medición 1 - Concurrencia I/O

Se descargaron 20 URLs de forma secuencial y luego de forma concurrente.

Resultados
        Método	                 Tiempo
        Secuencial	             8.39 s
        Concurrente	             1.37 s
        Speedup                  6.11x

Conclusión
Las tareas I/O-bound se benefician mucho de la concurrencia. Mientras una descarga espera datos de la red, el event loop puede continuar trabajando con otras.

- Medición 2 - Event loop bloqueado
Se ejecutó una tarea CPU-bound pesada.

Sin executor
Operación	TiempoPOST /prueba-bloqueo	39.825 s
GET /tareas	38.414 s
Con executor (asyncio.to_thread)
Operación	TiempoPOST /prueba-executor	39.766 s
GET /tareas	0.125 s

Conclusión
Cuando el cálculo corre directamente dentro de una corrutina, bloquea el event loop.

Al moverlo a un thread usando:
asyncio.to_thread()
el cálculo tarda lo mismo, pero la API continúa respondiendo normalmente.

Esta fue una de las diferencias más interesantes observadas durante el trabajo.

Medición 3 - Techo del pool
Pool configurado con:
WorkerPool(worker_count=4)
Todas las tareas duraban 10 segundos.

Resultados
Cantidad de tareas	 Tiempo
        4	          11 s
        8	          23 s
        16	          42 s
        32	          84 s

Conclusión
El tiempo aumenta casi linealmente con la cantidad de tareas.
Esto ocurre porque solamente existen 4 workers. Cuando llegan más tareas que workers disponibles, las restantes quedan esperando en la asyncio.Queue.
El cuello de botella observado fue justamente el tamaño del pool.

CONCEPTOS DEL CURSO APLICADOS

Productor - consumidor:
La API genera tareas y los workers las consumen desde una cola compartida.
Se utilizó el mismo patrón visto en clase, pero implementado con corrutinas.

Event loop:
Toda la aplicación funciona sobre un único event loop de asyncio.
Los cambios de ejecución ocurren únicamente cuando aparece un:
await

Corrutinas
Los workers son corrutinas creadas mediante:
asyncio.create_task()

I/O Multiplexing
FastAPI y asyncio permiten atender múltiples conexiones concurrentemente utilizando el event loop sin crear un thread por cliente.

CPU-bound vs I/O-bound
El trabajo permitió observar claramente la diferencia entre:
operaciones de red (I/O-bound)
cálculos intensivos (CPU-bound)
y entender por qué asyncio resuelve muy bien una de ellas pero no la otra.

Persistencia
Al cerrar la aplicación:
CTRL + C
o mediante señales del sistema:
SIGINT, SIGTERM
se genera automáticamente un archivo: estado_<timestamp>.json
dentro de: dumps/

Además, al iniciar la aplicación se informa por log si existen dumps previos.

Cómo ejecutar el proyecto
Docker
Desde la raíz del proyecto: docker compose up --build
La API quedará disponible en: http://localhost:8000

Swagger:
http://localhost:8000/docs

LIMITACIONES CONOCIDAS
El estado vive únicamente en memoria.
No existe base de datos.
Si se reinicia la aplicación, las tareas en ejecución se pierden.
Las tareas CPU-bound enviadas a threads pueden seguir ejecutándose aunque la tarea haya sido marcada como cancelada.
No existe límite de tamaño para la cola de tareas.

LO QUE APRENDÍ
Este trabajo me ayudó a entender mucho mejor para qué sirve realmente asyncio y cuáles son sus límites.
Antes de hacerlo pensaba que asyncio resolvía cualquier problema de concurrencia, pero durante la implementación pude ver que funciona muy bien para operaciones I/O-bound y que para tareas CPU-bound es necesario utilizar threads o procesos para evitar bloquear el event loop.
También me sirvió para entender mejor el patrón productor-consumidor, el uso de colas compartidas y cómo se puede construir un sistema que atienda muchas tareas concurrentemente sin crear un thread por cada una.
Por último, trabajar con Docker fue útil porque permitió ejecutar toda la aplicación de forma reproducible y simplificó bastante la puesta en marcha del proyecto.
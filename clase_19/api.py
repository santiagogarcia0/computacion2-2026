#!/usr/bin/env python3
import asyncio
import os
import threading
from typing import Literal

from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field

app = FastAPI(
    title='Tareas',
    description='Ejemplo de la clase 19: HTTP + FastAPI',
)

tareas: dict[int, dict] = {}
proximo_id = 0

# ---------------------------------------------------------------
# Modelos
# ---------------------------------------------------------------

class TareaNueva(BaseModel):
    tipo: Literal['descargar', 'hashear', 'esperar']
    prioridad: int = Field(default=1, ge=1, le=5, description='1 = más baja, 5 = más alta')


class Tarea(TareaNueva):
    id: int
    estado: Literal['pendiente', 'ejecutando', 'completada'] = 'pendiente'


# NUEVO MODELO PARA PATCH: Todos los campos que se quieran actualizar
class TareaUpdate(BaseModel):
    estado: Literal['pendiente', 'ejecutando', 'completada']


# ---------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------

@app.get('/')
async def raiz():
    return {'servicio': 'tareas', 'docs': '/docs'}


@app.get('/tareas', response_model=list[Tarea])
async def listar(
    estado: str | None = Query(default=None, description='Filtrar por estado'),
    limite: int = Query(default=10, ge=1, le=100),
):
    items = list(tareas.values())
    if estado:
        items = [t for t in items if t['estado'] == estado]
    return items[:limite]


@app.post('/tareas', response_model=Tarea, status_code=201)
async def crear(nueva: TareaNueva):
    global proximo_id
    
    # NUEVA VALIDACIÓN: Rechazar si ya hay 10 pendientes
    pendientes = [t for t in tareas.values() if t['estado'] == 'pendiente']
    if len(pendientes) >= 10:
        # Usamos 400 Bad Request o 409 Conflict. 409 es ideal porque denota un conflicto
        # con el estado actual del servidor (la cola está llena de ítems en ese estado).
        raise HTTPException(
            status_code=409, 
            detail='No se pueden agregar más tareas: el límite de 10 pendientes fue alcanzado.'
        )

    proximo_id += 1
    tarea = {'id': proximo_id, **nueva.model_dump(), 'estado': 'pendiente'}
    tareas[proximo_id] = tarea
    return tarea


@app.get('/tareas/{tarea_id}', response_model=Tarea)
async def obtener(tarea_id: int):
    if tarea_id not in tareas:
        raise HTTPException(status_code=404, detail='No existe esa tarea')
    return tareas[tarea_id]


# NUEVO ENDPOINT: Cambiar solo el estado de la tarea
@app.patch('/tareas/{tarea_id}', response_model=Tarea)
async def actualizar_estado(tarea_id: int, actualizacion: TareaUpdate):
    if tarea_id not in tareas:
        raise HTTPException(status_code=404, detail='No existe esa tarea')
    
    # Modificamos únicamente el estado
    tareas[tarea_id]['estado'] = actualizacion.estado
    return tareas[tarea_id]


# NUEVO ENDPOINT: Estadísticas de tareas por estado
@app.get('/estadisticas')
async def obtener_estadisticas():
    conteo = {'pendiente': 0, 'ejecutando': 0, 'completada': 0}
    for t in tareas.values():
        conteo[t['estado']] += 1
    return conteo


@app.delete('/tareas/{tarea_id}', status_code=204)
async def borrar(tarea_id: int):
    if tarea_id not in tareas:
        raise HTTPException(status_code=404, detail='No existe esa tarea')
    del tareas[tarea_id]


@app.get('/quien-soy')
async def quien_soy():
    loop = asyncio.get_running_loop()
    return {
        'pid': os.getpid(),
        'thread': threading.current_thread().name,
        'loop': type(loop).__name__,
        'id_del_loop': id(loop),
    }


@app.get('/quien-soy-sync')
def quien_soy_sync():
    try:
        asyncio.get_running_loop()
        estado = 'HAY loop'
    except RuntimeError:
        estado = 'NO hay loop corriendo acá'
    return {'thread': threading.current_thread().name, 'loop': estado}


if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='127.0.0.1', port=8000)

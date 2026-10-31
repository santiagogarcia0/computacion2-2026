from fastapi import APIRouter, HTTPException

from app.core.container import task_manager
from app.models.schemas import TaskCreateRequest
from app.models.task import TaskStatus

router = APIRouter()


@router.post("/tareas")
async def create_task(request: TaskCreateRequest):

    task = await task_manager.create_task(
        task_type=request.type,
        payload=request.payload,
        timeout=request.timeout
    )

    return {
        "id": task.id,
        "status": task.status
    }


@router.get("/tareas")
async def get_tasks(status: str | None = None):

    tasks = task_manager.list_tasks()

    if status:

        tasks = [
            task
            for task in tasks
            if task.status == status
        ]

    return [
        {
            "id": task.id,
            "type": task.task_type,
            "status": task.status,
            "timeout": task.timeout,
            "created_at": task.created_at
        }
        for task in tasks
    ]


@router.get("/tareas/{task_id}")
async def get_task(task_id: str):

    task = task_manager.get_task(task_id)

    if task is None:
        raise HTTPException(404, "Tarea no encontrada")

    return task.__dict__


@router.delete("/tareas/{task_id}")
async def cancel_task(task_id: str):

    success = await task_manager.cancel_task(
        task_id
    )

    if not success:
        raise HTTPException(
            status_code=404,
            detail="Tarea no encontrada"
        )

    return {
        "mensaje": "Tarea cancelada"
    }


""" ENDPOINTS DE PRUEBA

from scripts.hash_sin_executor import hash_pesado_sin_executor
@router.post("/prueba-bloqueo")
async def prueba_bloqueo():

    await hash_pesado_sin_executor()

    return {
        "resultado": "terminado"
    }


from scripts.hash_con_executor import (
    hash_pesado_con_executor
)
@router.post("/prueba-executor")
async def prueba_executor():

    await hash_pesado_con_executor()

    return {
        "resultado": "terminado"
    }"""
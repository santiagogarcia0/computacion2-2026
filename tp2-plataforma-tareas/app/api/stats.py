from fastapi import APIRouter

from app.core.container import task_manager
from app.models.task import TaskStatus

router = APIRouter()


@router.get("/estadisticas")
async def get_stats():

    tasks = list(task_manager.tasks.values())

    total = len(tasks)

    stats = {
        status.value: 0
        for status in TaskStatus
    }

    durations = []

    for task in tasks:

        stats[task.status.value] += 1

        if (
            task.started_at and
            task.finished_at
        ):

            durations.append(
                (
                    task.finished_at -
                    task.started_at
                ).total_seconds()
            )

    avg_time = (
        sum(durations) / len(durations)
        if durations
        else 0
    )

    return {
        "total_tareas": total,
        "workers_ocupados": len(
            task_manager.running_coroutines
        ),
        "promedio_segundos": round(
            avg_time,
            2
        ),
        "por_estado": stats
    }
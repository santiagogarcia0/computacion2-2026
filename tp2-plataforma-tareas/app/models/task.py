from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
from typing import Any, Optional


class TaskStatus(str, Enum):
    """
    Estados posibles de una tarea.

    pendiente:
        Está en la cola esperando un worker.

    ejecutando:
        Algún worker la está procesando.

    completada:
        Terminó correctamente.

    fallida:
        Terminó con error o timeout.

    cancelada:
        El usuario solicitó su cancelación.
    """

    PENDING = "pendiente"
    RUNNING = "ejecutando"
    COMPLETED = "completada"
    FAILED = "fallida"
    CANCELLED = "cancelada"


@dataclass
class Task:
    """
    Modelo interno de una tarea.
    """

    id: str
    task_type: str
    payload: dict

    status: TaskStatus = TaskStatus.PENDING

    created_at: datetime = field(default_factory=datetime.utcnow)

    started_at: Optional[datetime] = None
    finished_at: Optional[datetime] = None

    result: Any = None
    error: Optional[str] = None

    timeout: int = 60
import asyncio
import uuid

from app.models.task import Task
from app.models.task import TaskStatus


class TaskManager:
    """
    Mantiene:

    - Diccionario de tareas
    - Cola de ejecución
    - Referencias a corrutinas ejecutándose
    """

    def __init__(self):

        self.tasks: dict[str, Task] = {}

        self.queue = asyncio.Queue()

        self.running_coroutines = {}

    async def create_task(
        self,
        task_type: str,
        payload: dict,
        timeout: int
    ):

        task_id = str(uuid.uuid4())

        task = Task(
            id=task_id,
            task_type=task_type,
            payload=payload,
            timeout=timeout
        )

        self.tasks[task_id] = task

        await self.queue.put(task_id)

        return task

    def get_task(self, task_id: str):

        return self.tasks.get(task_id)

    def list_tasks(self):

        return list(self.tasks.values())

    async def cancel_task(self, task_id: str):

        task = self.tasks.get(task_id)

        if task is None:
            return False

        running = self.running_coroutines.get(task_id)

        if running:
            running.cancel()

        task.status = TaskStatus.CANCELLED

        return True
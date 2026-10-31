import asyncio
from datetime import datetime

from app.models.task import TaskStatus
from app.core.container import task_manager
from app.services.wait_task import execute_wait_task
from app.services.download_task import execute_download_task
from app.services.hash_task import execute_hash_task



class WorkerPool:
    """
    Pool de workers asincrónicos.

    Cada worker consume tareas desde la misma queue.
    """

    def __init__(self, worker_count: int = 4):

        self.worker_count = worker_count

        self.workers = []

    async def start(self):

        print(f"Iniciando {self.worker_count} workers...")

        for i in range(self.worker_count):

            worker = asyncio.create_task(
                self.worker_loop(i)
            )

            self.workers.append(worker)

    async def worker_loop(self, worker_id: int):

        while True:

            task_id = await task_manager.queue.get()

            task = task_manager.get_task(task_id)

            if task is None:
                continue

            if task.status == TaskStatus.CANCELLED:
                continue

            try:

                print(
                    f"[WORKER {worker_id}] Ejecutando tarea {task.id}"
                )

                task.status = TaskStatus.RUNNING
                task.started_at = datetime.utcnow()

                execution_task = asyncio.create_task(
                    self.execute_task(task)
                )

                task_manager.running_coroutines[
                    task.id
                ] = execution_task

                await asyncio.wait_for(
                    execution_task,
                    timeout=task.timeout
                )

            except asyncio.TimeoutError:

                task.status = TaskStatus.FAILED
                task.error = "Timeout excedido"

            except asyncio.CancelledError:

                print(
                    f"[WORKER {worker_id}] Tarea {task.id} cancelada"
                )

                task.status = TaskStatus.CANCELLED
                task.result = None

            except Exception as e:

                task.status = TaskStatus.FAILED
                task.error = str(e)

            finally:

                task.finished_at = datetime.utcnow()

                task_manager.running_coroutines.pop(
                    task.id,
                    None
                )

                task_manager.queue.task_done()

    async def execute_task(self, task):
        """
        Ejecuta una tarea según su tipo.

        Si la tarea es cancelada, propagamos la excepción
        para que el worker la marque correctamente.
        """

        try:

            if task.task_type == "esperar":

                result = await execute_wait_task(
                    task.payload
                )

            elif task.task_type == "descargar":

                result = await execute_download_task(
                    task.payload
                )

            elif task.task_type == "hashear":

                result = await execute_hash_task(
                    task.payload
                ) 

            else:

                raise Exception(
                    f"Tipo de tarea desconocido: {task.task_type}"
                )

            # Evita sobrescribir una cancelación
            if task.status != TaskStatus.CANCELLED:

                task.result = result
                task.status = TaskStatus.COMPLETED

        except asyncio.CancelledError:

            print(f"Tarea {task.id} cancelada")

            task.status = TaskStatus.CANCELLED
            task.result = None

            raise
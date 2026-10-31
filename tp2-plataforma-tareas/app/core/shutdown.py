import json
from datetime import datetime
from pathlib import Path

from app.core.container import task_manager


async def save_state():
    """
    Guarda todas las tareas
    al apagar la aplicación.
    """

    Path("dumps").mkdir(
        exist_ok=True
    )

    timestamp = datetime.now().strftime(
        "%Y%m%d_%H%M%S"
    )

    filename = (
        f"dumps/estado_{timestamp}.json"
    )

    data = []

    for task in task_manager.tasks.values():

        data.append({
            "id": task.id,
            "type": task.task_type,
            "status": task.status,
            "result": task.result,
            "error": task.error
        })

    with open(
        filename,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            data,
            file,
            indent=4,
            ensure_ascii=False
        )

    print(
        f"Estado guardado en {filename}"
    )


def report_previous_dumps():
    """
    Informa si existen volcados previos.
    """

    dumps = list(
        Path("dumps").glob("estado_*.json")
    )

    if dumps:

        print(
            f"Se encontraron {len(dumps)} dump(s) previo(s):"
        )

        for dump in dumps:

            print(
                f" - {dump.name}"
            )
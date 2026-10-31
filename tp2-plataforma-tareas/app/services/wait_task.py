import asyncio


async def execute_wait_task(payload: dict):
    """
    Simula una operación I/O.

    Esto NO bloquea el event loop.
    """

    seconds = payload["seconds"]

    await asyncio.sleep(seconds)

    return {
        "mensaje": f"Esperé {seconds} segundos"
    }
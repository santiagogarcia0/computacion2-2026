import hashlib
import asyncio


def hash_worker(text, iterations):
    """
    Función CPU-bound.

    Corre fuera del event loop.
    """

    current = text

    for _ in range(iterations):

        current = hashlib.sha256(
            current.encode()
        ).hexdigest()

    return current


async def execute_hash_task(payload):

    text = payload["text"]

    iterations = payload["iterations"]

    result = await asyncio.to_thread(
        hash_worker,
        text,
        iterations
    )

    return {
        "hash": result,
        "iterations": iterations
    }
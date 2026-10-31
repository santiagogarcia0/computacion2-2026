import hashlib
import asyncio


def hash_worker():

    texto = "hola"

    for _ in range(50_000_000):

        texto = hashlib.sha256(
            texto.encode()
        ).hexdigest()

    return texto


async def hash_pesado_con_executor():

    return await asyncio.to_thread(
        hash_worker
    )
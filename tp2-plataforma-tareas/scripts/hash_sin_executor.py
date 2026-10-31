import hashlib


async def hash_pesado_sin_executor():

    texto = "hola"

    for _ in range(50_000_000):

        texto = hashlib.sha256(
            texto.encode()
        ).hexdigest()

    return texto

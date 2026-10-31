import hashlib
import time


def hash_pesado():

    texto = "hola"

    for _ in range(5_000_000):

        texto = hashlib.sha256(
            texto.encode()
        ).hexdigest()


inicio = time.perf_counter()

hash_pesado()

fin = time.perf_counter()

print(fin - inicio)
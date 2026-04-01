import time
from functools import wraps

def retry(max_attempts=3, delay=1, exceptions=(Exception,)):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None

            for intento in range(1, max_attempts + 1):
                try:
                    return func(*args, **kwargs)

                except exceptions as e:
                    last_exception = e

                    if intento < max_attempts:
                        print(f"Intento {intento}/{max_attempts} falló: {e}. Esperando {delay}s...")
                        time.sleep(delay)
                    else:
                        print(f"Intento {intento}/{max_attempts} falló: {e}.")

            # Si llega acá, fallaron todos
            raise last_exception

        return wrapper
    return decorator

import random

@retry(max_attempts=3, delay=1)
def conectar_servidor():
    if random.random() < 0.7:
        raise ConnectionError("Servidor no disponible")
    return "Conectado exitosamente"


try:
    print(conectar_servidor())
except ConnectionError:
    print("Falló después de 3 intentos")
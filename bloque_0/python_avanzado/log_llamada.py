from functools import wraps
from datetime import datetime

def log_llamada(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        # timestamp
        ahora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # formatear argumentos
        args_str = ", ".join(repr(a) for a in args)
        kwargs_str = ", ".join(f"{k}={repr(v)}" for k, v in kwargs.items())

        # combinar ambos
        params = ", ".join(filter(None, [args_str, kwargs_str]))

        print(f"[{ahora}] Llamando a {func.__name__}({params})")

        resultado = func(*args, **kwargs)

        print(f"[{ahora}] {func.__name__} retornó {repr(resultado)}")

        return resultado

    return wrapper

@log_llamada
def sumar(a, b):
    return a + b

sumar(3, 5)
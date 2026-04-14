import redis
import time
import os

redis_host = os.getenv("REDIS_HOST", "redis")
r = redis.Redis(host=redis_host, port=6379)

print("Worker iniciado...")

while True:
    valor = r.incr("contador")
    print(f"Contador actualizado: {valor}")
    time.sleep(1)
from flask import Flask
import redis
import os

app = Flask(__name__)

redis_host = os.getenv("REDIS_HOST", "redis")
r = redis.Redis(host=redis_host, port=6379)

@app.route("/")
def index():
    try:
        contador = r.get("contador")
        contador = int(contador) if contador else 0
    except:
        contador = "Error conectando a Redis"

    return f"""
    <h1>Servidor Web en Docker</h1>
    <p>Contador: {contador}</p>
    """

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
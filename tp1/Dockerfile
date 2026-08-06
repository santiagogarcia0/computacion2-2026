# Usamos la imagen oficial ligera de Python basada en Linux Debian Slim
FROM python:3.11-slim

# Configuramos variables de entorno para que Python no guarde caché 
# y maneje los textos en UTF-8 sin romper la TUI de Rich
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV LANG=C.UTF-8
ENV LC_ALL=C.UTF-8

# Establecemos la carpeta de trabajo adentro del contenedor
WORKDIR /app

# Copiamos la lista de requerimientos e instalamos la librería rich
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiamos todo el código fuente del proyecto adentro del contenedor
COPY src/ ./src/
COPY config.json .

# Nos paramos adentro de la carpeta src para que los imports de Python funcionen igual que en tu máquina
WORKDIR /app/src

# Comando por defecto que se ejecutará al arrancar el contenedor
CMD ["python3", "main.py"]

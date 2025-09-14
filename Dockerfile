# Usa una imagen base de Python 3.11 optimizada (slim).
FROM python:3.11-slim

# Establece el directorio de trabajo en /app.
WORKDIR /app

# Copia el archivo de dependencias.
COPY requirements.txt .

# Instala las dependencias de Python definidas en requirements.txt.
# --no-cache-dir evita guardar el caché de pip, reduciendo el tamaño de la imagen.
RUN pip install --no-cache-dir -r requirements.txt

# Copia el resto de los archivos de la aplicación al directorio de trabajo.
COPY . .

# El comando para iniciar la aplicación se especifica en docker-compose.yml.
# Esto permite que el Dockerfile sea reutilizable si decidimos añadir más servicios.

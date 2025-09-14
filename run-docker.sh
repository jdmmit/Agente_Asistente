#!/bin/bash

# run-docker.sh - Configura el entorno (si es necesario) y ejecuta Docker

set -e

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# --- 1. Configuración del Entorno (.env) ---
# Solo ejecuta el script de configuración si el archivo .env no existe.
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}--- No se encontró .env, iniciando la configuración del entorno ---${NC}"
    # Asegurarse de que el script de configuración sea ejecutable
    if [ ! -x "utils/secure-env.sh" ]; then
        chmod +x utils/secure-env.sh
    fi
    ./utils/secure-env.sh
else
    echo -e "${GREEN}--- Se encontró archivo .env, saltando configuración ---${NC}"
fi

# --- 2. Iniciar Docker ---
echo -e "${GREEN}--- Iniciando Docker Compose ---${NC}"
echo "Construyendo las imágenes y levantando los servicios..."
# Usa el comando moderno 'docker compose'
docker compose up --build -d

echo
echo -e "${GREEN}--- ¡Listo! ---${NC}"
echo "La interfaz web de Memorae debería estar disponible en:"
echo "http://localhost:8501"
echo
echo "Puedes ver los logs con: docker compose logs -f"

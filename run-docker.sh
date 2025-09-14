#!/bin/bash

# run-docker.sh - Gestiona la configuración del entorno y el lanzamiento de Docker.

# --- Colores para la salida ---
C_GREEN='\033[0;32m'
C_BLUE='\033[0;34m'
C_YELLOW='\033[1;33m'
C_RED='\033[0;31m'
C_NC='\033[0m' # No Color

# --- Lógica Principal ---

# Comprobar si el archivo .env existe
if [ ! -f ".env" ]; then
    # Si no existe, creamos la plantilla e instruimos al usuario
    echo -e "${C_YELLOW}--- No se encontró archivo .env ---${C_NC}"

    # Ejecutar el script que crea la plantilla .env.example
    if [ -f "utils/secure-env.sh" ]; then
        bash utils/secure-env.sh
    else
        echo -e "${C_RED}Error: El script 'utils/secure-env.sh' no se encontró. Abortando.${C_NC}"
        exit 1
    fi

    echo
    echo -e "${C_YELLOW}---------------- ACCIÓN REQUERIDA ----------------${C_NC}"
    echo "He creado un archivo de plantilla llamado '.env.example' en tu directorio."
    echo
    echo "Por favor, sigue estos 3 pasos:"
    echo "1. Renombra el archivo:   ${C_GREEN}mv .env.example .env${C_NC}"
    echo "2. Ábrelo y edita los valores con tus propias credenciales."
    echo "3. Vuelve a ejecutar el instalador:   ${C_GREEN}bash install.sh${C_NC}"
    echo -e "${C_YELLOW}----------------------------------------------------${C_NC}"
    echo
    # Salir del script para que el usuario pueda completar los pasos manuales
    exit 0
fi

# Si .env ya existe, procedemos a iniciar Docker.
echo -e "${C_GREEN}--- Se encontró archivo .env, saltando configuración ---${C_NC}"
echo -e "${C_YELLOW}--- Iniciando Docker Compose ---${C_NC}"
echo "Construyendo las imágenes y levantando los servicios..."

# Comando para levantar Docker Compose
docker compose up --build -d

if [ $? -eq 0 ]; then
    echo -e "${C_GREEN}¡Éxito! La aplicación se está ejecutando en segundo plano.${C_NC}"
    echo "Puedes ver la interfaz web en: ${C_BLUE}http://localhost:8501${C_NC}"
    echo "Para detener la aplicación, ejecuta: ${C_YELLOW}docker compose down${C_NC}"
else
    echo -e "${C_RED}Error: Fallo al iniciar Docker Compose.${C_NC}"
    echo "Revisa los mensajes de error de arriba para más detalles."
    exit 1
fi

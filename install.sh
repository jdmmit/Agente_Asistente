#!/bin/bash

# install.sh - Script principal para instalar y configurar el proyecto

set -e # Salir inmediatamente si un comando falla

# --- Colores para la Salida ---
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # Sin color

# --- Bienvenida ---
echo -e "${GREEN}==============================================${NC}"
echo -e "${GREEN}    Bienvenido al Instalador de Memorae       ${NC}"
echo -e "${GREEN}==============================================${NC}"
echo -e "Este script te guiará a través de la instalación completa del asistente."
echo -e "Se instalarán las dependencias, se configurará tu entorno y se iniciará la aplicación con Docker."
echo

# --- Permisos y Ejecución del Script Principal ---

# Asegurarse de que el script run-docker.sh sea ejecutable
if [ ! -x "run-docker.sh" ]; then
    echo -e "${YELLOW}Otorgando permisos de ejecución a 'run-docker.sh'...${NC}"
    chmod +x run-docker.sh
fi

# Ejecutar el script principal que maneja la configuración y el inicio de Docker
echo -e "${YELLOW}Iniciando el script de configuración y ejecución de Docker...${NC}"
./run-docker.sh

echo
echo -e "${GREEN}==============================================${NC}"
echo -e "${GREEN} ¡Instalación y Arranque Completados!      ${NC}"

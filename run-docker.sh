#!/bin/bash

# run-docker.sh - Script para ejecutar Docker Compose con manejo de permisos (Corregido para sudo siempre si necesario)

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${YELLOW}Verificando Docker...${NC}"

# Iniciar Docker daemon si no corre
if ! systemctl is-active --quiet docker; then
    echo -e "${YELLOW}Iniciando Docker daemon...${NC}"
    sudo systemctl start docker
    sudo systemctl enable docker
fi

# Test si docker funciona sin sudo
if docker info > /dev/null 2>&1; then
    echo -e "${GREEN}Docker accesible sin sudo.${NC}"
    DOCKER_CMD="docker compose"
else
    echo -e "${YELLOW}Usando sudo para Docker (permisos requeridos).${NC}"
    DOCKER_CMD="sudo docker compose"
fi

# Build and run
echo -e "${YELLOW}Ejecutando ${DOCKER_CMD} up --build...${NC}"
${DOCKER_CMD} up --build

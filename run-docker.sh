#!/bin/bash

# run-docker.sh - Configura el entorno y ejecuta Docker Compose

set -e # Salir si un comando falla

# --- Colores para la Salida ---
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # Sin color

# --- Paso 1: Configuración del Entorno ---
echo -e "${GREEN}--- Iniciando la configuración del entorno ---${NC}"

# Asegurarse de que el script de configuración sea ejecutable
if [ ! -x "utils/secure-env.sh" ]; then
    echo -e "${YELLOW}Otorgando permisos de ejecución a 'utils/secure-env.sh'...${NC}"
    chmod +x utils/secure-env.sh
fi

# Ejecutar el script de configuración interactivo
./utils/secure-env.sh

# Verificar si el archivo .env fue creado
if [ ! -f ".env" ]; then
    echo -e "${RED}Error: El archivo '.env' no fue creado. La configuración falló.${NC}"
    echo -e "${YELLOW}Por favor, ejecuta 'utils/secure-env.sh' manualmente para diagnosticar el problema.${NC}"
    exit 1
fi

echo -e "${GREEN}--- Configuración del entorno completada ---${NC}\n"


# --- Paso 2: Verificación y Ejecución de Docker ---
echo -e "${GREEN}--- Iniciando Docker ---${NC}"

# Verificar si Docker está instalado y activo
if ! command -v docker &> /dev/null; then
    echo -e "${RED}Error: Docker no está instalado.${NC}"
    echo -e "${YELLOW}Por favor, instala Docker y vuelve a ejecutar este script.${NC}"
    exit 1
fi

# Iniciar el daemon de Docker si no está activo (en sistemas con systemd)
if command -v systemctl &> /dev/null && ! systemctl is-active --quiet docker; then
    echo -e "${YELLOW}Iniciando el servicio de Docker...${NC}"
    # Usar sudo para iniciar y habilitar Docker
    if sudo systemctl start docker && sudo systemctl enable docker; then
        echo -e "${GREEN}Servicio de Docker iniciado correctamente.${NC}"
    else
        echo -e "${RED}Error al iniciar el servicio de Docker. Puede que necesites hacerlo manualmente.${NC}"
        exit 1
    fi
    # Esperar un momento para que el servicio se estabilice
    sleep 3
fi

# Determinar si se necesita sudo para ejecutar Docker Compose
DOCKER_CMD="docker compose"
if ! docker info > /dev/null 2>&1; then
    echo -e "${YELLOW}Se requieren permisos de administrador para Docker. Usando 'sudo'.${NC}"
    DOCKER_CMD="sudo docker compose"
fi

# Construir e iniciar los contenedores
echo -e "${YELLOW}Ejecutando '${DOCKER_CMD} up --build'...${NC}"
echo -e "Esto puede tardar varios minutos la primera vez."

if ${DOCKER_CMD} up --build; then
    echo -e "${GREEN}¡El asistente se está ejecutando en Docker!${NC}"
else
    echo -e "${RED}Error al ejecutar Docker Compose. Revisa los mensajes de error anteriores.${NC}"
    exit 1
fi

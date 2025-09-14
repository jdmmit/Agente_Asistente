#!/bin/bash
#
# Script principal de instalación para Memorae.
# Ofrece la opción de instalar y ejecutar con Docker o de forma local.

# --- Configuración de Colores ---
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# --- Verificación de Prerrequisitos ---
check_docker() {
    if ! command -v docker &> /dev/null; then
        echo -e "${RED}Error: Docker no está instalado o no se encuentra en el PATH.${NC}"
        echo -e "Por favor, instálalo desde ${CYAN}https://docs.docker.com/get-docker/${NC}"
        return 1
    fi
    # Comprobamos 'docker compose' y el antiguo 'docker-compose'
    if ! (command -v docker-compose &> /dev/null || docker compose version &> /dev/null); then
        echo -e "${RED}Error: Docker Compose no está instalado o no se encuentra en el PATH.${NC}"
        echo -e "Es necesario para ejecutar la aplicación con Docker."
        return 1
    fi
    return 0
}

# --- Menú Principal ---
show_main_menu() {
    echo -e "\n${CYAN}--- Instalador de Memorae ---${NC}"
    echo -e "Elige cómo quieres instalar y ejecutar la aplicación:"
    echo ""
    echo -e "1. ${GREEN}Con Docker (Recomendado)${NC} - Fácil y autocontenido. Se encarga de todo."
    echo -e "2. ${YELLOW}De forma Local${NC} - Para desarrolladores o si no quieres usar Docker."
    echo "3. Salir"
    echo -e "${CYAN}-------------------------------${NC}"
}

while true; do
    show_main_menu
    read -p "Selecciona una opción (1-3): " main_choice

    case $main_choice in
        1)
            echo -e "\n${GREEN}Iniciando instalación con Docker...${NC}"
            if ! check_docker; then
                echo -e "\nNo se pudo proceder con la instalación de Docker. Por favor, revisa los errores."
                continue
            fi
            echo -e "\nConstruyendo y levantando los contenedores... (Esto puede tardar unos minutos la primera vez)"
            
            # Usamos 'docker compose' si está disponible, si no, el antiguo 'docker-compose'
            if docker compose version &> /dev/null; then
                docker compose up --build
            else
                docker-compose up --build
            fi

            if [ $? -ne 0 ]; then
                echo -e "\n${RED}Hubo un error durante la ejecución de Docker Compose.${NC}"
                echo "Revisa la salida para más detalles."
            fi
            echo -e "\nHas detenido los contenedores de Docker."
            ;;
        2)
            echo -e "\n${YELLOW}Iniciando instalación local...${NC}"
            chmod +x scripts/setup-local.sh
            ./scripts/setup-local.sh
            echo -e "\n${GREEN}El script de instalación local ha finalizado.${NC}"
            break
            ;;
        3)
            echo -e "\n${GREEN}¡Hasta luego!${NC}"
            break
            ;;
        *)
            echo -e "\n${RED}Opción no válida. Por favor, selecciona 1, 2 o 3.${NC}"
            ;;
    esac
done

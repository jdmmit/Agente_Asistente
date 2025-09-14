#!/bin/bash
#
# Script principal de instalación y diagnóstico para Memorae.
# Ofrece la opción de instalar con Docker o localmente, y verifica la integridad de ambas instalaciones.

# --- Configuración de Colores y Variables ---
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
RED='\033[0;31m'
NC='\033[0m' # No Color

VENV_DIR=".venv"
OS="$(uname)"
PYTHON_CMD=""
OLLAMA_HOST_URL="http://localhost:11434"

# --- Funciones de Ayuda ---

detect_python_command() {
    if command -v python3 &> /dev/null; then PYTHON_CMD="python3";
    elif command -v python &> /dev/null; then PYTHON_CMD="python";
    else return 1; fi
    return 0
}

check_docker_running() {
    if ! command -v docker &> /dev/null; then
        echo -e "${RED}Error: Docker no está instalado.${NC} Visita ${CYAN}https://docs.docker.com/get-docker/${NC}"
        return 1
    fi
    if ! docker info &> /dev/null; then
        echo -e "${RED}Error: El servicio de Docker no está en ejecución.${NC}"
        echo "Por favor, inicia el demonio de Docker e inténtalo de nuevo."
        return 1
    fi
    if ! (command -v docker-compose &> /dev/null || docker compose version &> /dev/null); then
        echo -e "${RED}Error: Docker Compose no está instalado.${NC}"
        return 1
    fi
    return 0
}

check_ollama_running() {
    if ! command -v curl &> /dev/null; then return 0; fi # No podemos verificar sin curl

    if ! curl -s --fail ${OLLAMA_HOST_URL} > /dev/null; then
        echo -e "\n${YELLOW}Advertencia: No se pudo conectar a Ollama en ${OLLAMA_HOST_URL}.${NC}"
        echo "Las pruebas que dependen de la IA podrían fallar."
        echo -e "Asegúrate de que Ollama esté en ejecución antes de continuar.${NC}"
        read -p "¿Quieres continuar de todas formas? (s/N): " consent
        if [[ "$consent" != "s" && "$consent" != "S" ]]; then
            return 1
        fi
    fi
    return 0
}

run_tests() {
    echo -e "\n${CYAN}--- Ejecutando Pruebas Automatizadas ---${NC}"
    if ! check_ollama_running; then return 1; fi
    chmod +x run-tests.sh
    ./run-tests.sh
    return $?
}

verify_docker_install() {
    echo -e "\n${CYAN}--- Verificando la Instalación de Docker ---${NC}"
    echo "Esperando a que los servicios se inicien (20 segundos)..."
    sleep 20

    if ! command -v curl &> /dev/null; then
        echo -e "${YELLOW}Advertencia: 'curl' no está instalado. No se puede verificar la interfaz web.${NC}"
        echo -e "Si todo fue bien, accede a la app en ${CYAN}http://localhost:8501${NC}"
        return
    fi

    echo "Intentando acceder a la interfaz web en http://localhost:8501..."
    if curl -s --head --fail http://localhost:8501 > /dev/null; then
        echo -e "${GREEN}¡Verificación de Docker exitosa! La interfaz web está respondiendo. ✅${NC}"
        echo -e "Accede a ella en: ${CYAN}http://localhost:8501${NC}"
    else
        echo -e "${RED}La verificación de Docker falló. La interfaz web no responde. ❌${NC}"
        echo -e "Ejecuta ${CYAN}docker compose logs -f streamlit_app${NC} para investigar."
    fi
}

run_local_install() {
    echo -e "\n${YELLOW}Iniciando instalación local...${NC}"
    if ! detect_python_command; then
        echo -e "${RED}Error: No se encontró 'python3' o 'python'.${NC}"; return 1;
    fi
    echo -e "${GREEN}Python detectado: $($PYTHON_CMD --version)${NC}"

    if [ ! -d "$VENV_DIR" ]; then $PYTHON_CMD -m venv $VENV_DIR; fi
    VENV_PYTHON="$VENV_DIR/bin/python"
    if [[ "$OS" == "MINGW"* || "$OS" == "CYGWIN"* || "$OS" == "MSYS"* ]]; then
        VENV_PYTHON="$VENV_DIR/Scripts/python"
    fi

    echo -e "\nInstalando dependencias..."
    $VENV_PYTHON -m pip install --upgrade pip && $VENV_PYTHON -m pip install -r requirements.txt
    if [ $? -ne 0 ]; then echo -e "${RED}Error al instalar dependencias.${NC}"; return 1; fi

    if [ ! -f ".env" ]; then
        echo "DATABASE_NAME=memorae.db" > .env
        echo "OLLAMA_HOST=${OLLAMA_HOST_URL}" >> .env
    fi

    echo -e "${GREEN}Instalación local completada.${NC}"
    
    run_tests
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}¡Instalación local verificada y funciona! ✅${NC}"
    else
        echo -e "${RED}Las pruebas fallaron. Revisa los errores anteriores para más detalles.${NC}"
    fi
    return 0
}

# --- Menú Principal ---
show_main_menu() {
    echo -e "\n${CYAN}--- Instalador y Verificador de Memorae ---${NC}"
    echo -e "1. ${GREEN}Instalar/Verificar con Docker (Recomendado)${NC}"
    echo -e "2. ${YELLOW}Instalar/Verificar Localmente${NC}"
    echo "3. Salir"
    echo -e "${CYAN}---------------------------------------------${NC}"
}

while true; do
    show_main_menu
    read -p "Selecciona una opción (1-3): " main_choice

    case $main_choice in
        1)
            echo -e "\n${GREEN}Opción Docker seleccionada...${NC}"
            if ! check_docker_running; then continue; fi

            echo -e "\nConstruyendo y levantando contenedores en segundo plano..."
            if docker compose version &> /dev/null; then docker compose up --build -d; else docker-compose up --build -d; fi
            if [ $? -ne 0 ]; then echo -e "\n${RED}Error al iniciar Docker Compose.${NC}"; continue; fi

            verify_docker_install
            echo -e "\n${GREEN}Contenedores ejecutándose.${NC} Logs: ${CYAN}docker compose logs -f${NC} | Detener: ${CYAN}docker compose down${NC}"
            break
            ;;
        2)
            run_local_install
            echo -e "\nEl proceso de instalación/verificación local ha finalizado."
            break
            ;;
        3)
            echo -e "\n${GREEN}¡Hasta luego!${NC}"
            break
            ;;
        *)
            echo -e "\n${RED}Opción no válida.${NC}"
            ;;
    esac
done

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

# --- Funciones de Ayuda ---

detect_python_command() {
    if command -v python3 &> /dev/null; then PYTHON_CMD="python3";
    elif command -v python &> /dev/null; then PYTHON_CMD="python";
    else return 1; fi
    return 0
}

check_docker() {
    if ! command -v docker &> /dev/null; then
        echo -e "${RED}Error: Docker no está instalado.${NC} Visita ${CYAN}https://docs.docker.com/get-docker/${NC}"
        return 1
    fi
    if ! (command -v docker-compose &> /dev/null || docker compose version &> /dev/null); then
        echo -e "${RED}Error: Docker Compose no está instalado.${NC}"
        return 1
    fi
    return 0
}

run_tests() {
    echo -e "\n${CYAN}--- Ejecutando Pruebas Automatizadas ---${NC}"
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
        echo -e "Posibles causas:
- Un problema durante la construcción de la imagen.
- El puerto 8501 ya está en uso.
- El contenedor de la app falló al iniciar."
        echo -e "Ejecuta ${CYAN}docker compose logs -f streamlit_app${NC} para investigar."
    fi
}

run_local_install() {
    echo -e "\n${YELLOW}Iniciando instalación local...${NC}"
    if ! detect_python_command; then
        echo -e "${RED}Error: No se encontró 'python3' o 'python'.${NC}"
        echo "Por favor, instala Python 3.10+ y asegúrate de que esté en tu PATH."
        return 1
    fi
    echo -e "${GREEN}Python detectado: $($PYTHON_CMD --version)${NC}"

    if [ ! -d "$VENV_DIR" ]; then
        echo -e "\nCreando entorno virtual..."
        $PYTHON_CMD -m venv $VENV_DIR
    fi

    VENV_PYTHON="$VENV_DIR/bin/python"
    if [[ "$OS" == "MINGW"* || "$OS" == "CYGWIN"* || "$OS" == "MSYS"* ]]; then
        VENV_PYTHON="$VENV_DIR/Scripts/python"
    fi

    echo -e "\nInstalando dependencias..."
    $VENV_PYTHON -m pip install --upgrade pip
    $VENV_PYTHON -m pip install -r requirements.txt
    if [ $? -ne 0 ]; then echo -e "${RED}Error al instalar dependencias.${NC}"; return 1; fi

    if [ ! -f ".env" ]; then
        echo -e "\nCreando archivo .env..."
        echo "DATABASE_NAME=memorae.db" > .env
        echo "OLLAMA_HOST=http://localhost:11434" >> .env
    fi

    echo -e "${GREEN}Instalación local completada.${NC}"
    
    run_tests
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}¡Instalación local verificada y funciona! ✅${NC}"
    else
        echo -e "${YELLOW}Las pruebas fallaron. Reinstalando dependencias...${NC}"
        $VENV_PYTHON -m pip install --force-reinstall -r requirements.txt
        
        echo -e "\nVolviendo a ejecutar las pruebas..."
        run_tests
        if [ $? -eq 0 ]; then
            echo -e "${GREEN}¡La reinstalación solucionó el problema! Verificado. ✅${NC}"
        else
            echo -e "${RED}La auto-reparación falló. Las pruebas siguen sin pasar. ❌${NC}"
            echo -e "Causas: error en el código de las pruebas, o el servicio Ollama no está corriendo."
        fi
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
            if ! check_docker; then continue; fi

            echo -e "\nConstruyendo y levantando contenedores en segundo plano..."
            if docker compose version &> /dev/null; then
                docker compose up --build -d
            else
                docker-compose up --build -d
            fi

            if [ $? -ne 0 ]; then
                echo -e "\n${RED}Error al iniciar los contenedores con Docker Compose.${NC}"
                continue
            fi

            verify_docker_install
            
            echo -e "\n${GREEN}Los contenedores se están ejecutando en segundo plano.${NC}"
            echo -e "Para ver los logs, usa: ${CYAN}docker compose logs -f${NC}"
            echo -e "Para detener todo, usa: ${CYAN}docker compose down${NC}"
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

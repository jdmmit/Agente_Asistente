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
VENV_PYTHON="" # Se definirá en run_local_install
OLLAMA_HOST_URL="http://localhost:11434"

# --- Funciones de Ayuda ---

detect_python_command() {
    if command -v python3 &> /dev/null; then PYTHON_CMD="python3";
    elif command -v python &> /dev/null; then PYTHON_CMD="python";
    else return 1; fi
    return 0
}

check_docker_running() {
    # ... (código sin cambios) ...
}

check_ollama_running() {
    # ... (código sin cambios) ...
}

run_tests() {
    # ... (código sin cambios) ...
}

verify_docker_install() {
    # ... (código sin cambios) ...
}

show_run_menu() {
    echo -e "\n${CYAN}--- ¿Qué te gustaría hacer ahora? ---${NC}"
    echo "1. Ejecutar la Interfaz Web (Frontend + Backend)"
    echo "2. Ejecutar el Modo Interactivo (solo Terminal)"
    echo "3. Salir"

    while true; do
        read -p "Selecciona una opción (1-3): " run_choice
        case $run_choice in
            1)
                echo -e "\n${GREEN}Iniciando el servidor del agente (backend) en segundo plano...${NC}"
                # Iniciar el backend y redirigir su salida a un archivo de log
                $VENV_PYTHON jdmmitagente.py > backend.log 2>&1 &
                BACKEND_PID=$!
                echo "Backend iniciado con PID: $BACKEND_PID. Los logs se guardan en backend.log"

                # Configurar una trampa para detener el backend cuando el script termine
                trap "echo '\nDeteniendo el servidor del agente (PID: $BACKEND_PID)...'; kill $BACKEND_PID" EXIT

                echo -e "\n${GREEN}Iniciando la interfaz web (frontend)... (Presiona Ctrl+C para detener ambos servicios)${NC}"
                # Iniciar el frontend
                $VENV_PYTHON -m streamlit run streamlit_app.py

                # La trampa se ejecutará automáticamente al salir de streamlit
                break
                ;;
            2)
                echo -e "\n${GREEN}Iniciando el modo interactivo en la terminal...${NC}"
                # El modo interactivo no necesita la API, ya que se ejecuta en el mismo proceso
                $VENV_PYTHON main.py
                break
                ;;
            3)
                break
                ;;
            *)
                echo -e "\n${RED}Opción no válida.${NC}"
                ;;
        esac
    done
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
    local test_result=$? # Guardar resultado de las pruebas
    if [ $test_result -eq 0 ]; then
        echo -e "${GREEN}¡Instalación local verificada y funciona! ✅${NC}"
        show_run_menu # Mostrar menú para ejecutar la app
    else
        echo -e "${RED}Las pruebas fallaron. Revisa los errores anteriores para más detalles.${NC}"
    fi
    return 0
}

# --- Menú Principal ---
show_main_menu() {
    # ... (código sin cambios) ...
}

while true; do
    show_main_menu
    read -p "Selecciona una opción (1-3): " main_choice

    case $main_choice in
        1)
            # ... (código sin cambios) ...
            ;;
        2)
            run_local_install
            echo -e "\nEl proceso de instalación/verificación local ha finalizado."
            break
            ;;
        3)
            # ... (código sin cambios) ...
            ;;
        *)
            # ... (código sin cambios) ...
            ;;
    esac
done

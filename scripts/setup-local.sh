#!/bin/bash
#
# Este script configura el entorno de desarrollo local y ofrece un menú para ejecutar la aplicación.
# Es compatible con Linux, macOS y Windows (a través de Git Bash o WSL).

# --- Configuración y Detección del Entorno --- #

# Colores para la salida
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Detección del Sistema Operativo
OS="$(uname)"
PYTHON_CMD="python3"
VENV_PIP=".venv/bin/pip"

if [[ "$OS" == "MINGW"* || "$OS" == "CYGWIN"* || "$OS" == "MSYS"* ]]; then
    # Comandos para Windows usando un shell tipo Unix (Git Bash, etc.)
    PYTHON_CMD="python"
    VENV_PIP=".venv/Scripts/pip"
fi

# --- Verificación de Prerrequisitos --- #

if ! command -v $PYTHON_CMD &> /dev/null; then
    echo -e "${RED}Error: No se encontró el comando 'python3' o 'python'.${NC}"
    echo -e "Por favor, instala Python 3.10 o superior y asegúrate de que esté en tu PATH."
    exit 1
fi

# --- Ejecución de la Instalación --- #

# 1. Crear un entorno virtual
if [ ! -d ".venv" ]; then
    echo -e "${YELLOW}Creando entorno virtual en ./.venv...${NC}"
    $PYTHON_CMD -m venv .venv
    if [ $? -ne 0 ]; then
        echo -e "${RED}Error: No se pudo crear el entorno virtual.${NC}" >&2
        echo -e "Asegúrate de tener instalado el paquete de venv (ej. 'sudo apt install python3-venv' en Debian/Ubuntu)." >&2
        exit 1
    fi
else
    echo -e "${GREEN}Entorno virtual .venv ya existe. Saltando creación.${NC}"
fi

# 2. Instalar las dependencias
echo -e "${YELLOW}Instalando dependencias desde requirements.txt...${NC}"
$VENV_PIP install -r requirements.txt
if [ $? -ne 0 ]; then
    echo -e "${RED}Error: Falló la instalación de dependencias con pip.${NC}" >&2
    exit 1
fi

# 3. Crear archivo .env si no existe
if [ ! -f .env ]; then
    echo -e "\n${YELLOW}Configurando el archivo de entorno .env...${NC}"
    echo -e "Presiona Enter para usar el modelo de Ollama recomendado (${GREEN}llama3${NC})."
    read -p "Modelo de Ollama a utilizar: " ollama_model
    if [ -z "$ollama_model" ]; then
        ollama_model="llama3"
    fi

    echo "# Archivo de configuración autogenerado" > .env
    echo "OLLAMA_MODEL=${ollama_model}" >> .env
    echo "DATABASE_NAME=memorae.db" >> .env
    echo -e "${GREEN}Archivo .env creado con éxito con el modelo '${ollama_model}'.${NC}"
else
    echo -e "\n${GREEN}Archivo .env ya existente. Saltando configuración.${NC}"
fi

# --- Menú de Ejecución --- #

# Definir ejecutables del entorno virtual
PYTHON_EXEC=${VENV_PIP/pip/python}
STREAMLIT_EXEC=${VENV_PIP/pip/streamlit}

show_menu() {
    echo -e "\n${YELLOW}--- ¿Qué quieres hacer ahora? ---${NC}"
    echo "1. Iniciar Interfaz Web (Streamlit)"
    echo "2. Iniciar Modo Interactivo (Terminal)"
    echo "3. Salir"
    echo -e "${YELLOW}----------------------------------${NC}"
}

while true; do
    show_menu
    read -p "Selecciona una opción (1-3): " choice

    case $choice in
        1)
            echo -e "\n${GREEN}Iniciando Interfaz Web...${NC}"
            echo "Puedes detener el servidor en cualquier momento con CTRL+C."
            echo "Accede a la aplicación en tu navegador (normalmente http://localhost:8501)."
            $STREAMLIT_EXEC run streamlit_app.py
            ;;
        2)
            echo -e "\n${GREEN}Iniciando Modo Interactivo en la Terminal...${NC}"
            $PYTHON_EXEC jdmmitagente.py
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

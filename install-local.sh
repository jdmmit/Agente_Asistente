#!/bin/bash
#
# Este script configura el entorno de desarrollo local sin Docker.
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
VENV_PATH=".venv/bin/activate"
VENV_PIP=".venv/bin/pip"

if [[ "$OS" == "Linux"* || "$OS" == "Darwin"* ]]; then
    # Comandos para Linux y macOS (Darwin)
    VENV_ACTIVATE_CMD="source .venv/bin/activate"

elif [[ "$OS" == "MINGW"* || "$OS" == "CYGWIN"* || "$OS" == "MSYS"* ]]; then
    # Comandos para Windows usando un shell tipo Unix (Git Bash, etc.)
    PYTHON_CMD="python"
    VENV_ACTIVATE_CMD="source .venv/Scripts/activate" # Git Bash usa sintaxis de Linux para la activación
    VENV_PIP=".venv/Scripts/pip"

else
    echo -e "${RED}Sistema operativo no compatible para este script.${NC}"
    echo -e "En Windows, por favor, ejecuta este script usando ${YELLOW}Git Bash${NC} o a través de ${YELLOW}WSL${NC}."
    exit 1
fi

# --- Verificación de Prerrequisitos --- #

# Verificar si Python está instalado
if ! command -v $PYTHON_CMD &> /dev/null; then
    # Si python3 no existe, intenta con python
    if command -v python &> /dev/null; then
        PYTHON_CMD="python"
    else
        echo -e "${RED}Error: No se encontró el comando 'python' o 'python3'.${NC}"
        echo -e "Por favor, instala Python 3.8 o superior y asegúrate de que esté en tu PATH."
        exit 1
    fi
fi

# --- Ejecución de la Instalación --- #

# 1. Crear un entorno virtual
echo -e "${YELLOW}Creando entorno virtual en ./.venv con el comando '$PYTHON_CMD'...${NC}"
$PYTHON_CMD -m venv .venv
if [ $? -ne 0 ]; then
    echo -e "${RED}Error: No se pudo crear el entorno virtual.${NC}" >&2
    echo -e "Asegúrate de tener instalado el paquete de venv (ej. 'sudo apt install python3-venv' en Debian/Ubuntu)." >&2
    exit 1
fi

# 2. Instalar las dependencias usando el pip del entorno virtual
echo -e "${YELLOW}Instalando dependencias desde requirements.txt...${NC}"
$VENV_PIP install -r requirements.txt
if [ $? -ne 0 ]; then
    echo -e "${RED}Error: Falló la instalación de dependencias con pip.${NC}" >&2
    exit 1
fi

# --- Instrucciones Finales --- #

echo -e "\n${GREEN}¡Entorno local configurado con éxito!${NC}"
echo -e "\n${YELLOW}Para iniciar la aplicación, sigue estos pasos:${NC}"
echo "1. Abre una nueva terminal."
echo "2. Activa el entorno virtual ejecutando: ${GREEN}${VENV_ACTIVATE_CMD}${NC}"
echo "3. Inicia el servidor del agente ejecutando: ${GREEN}python jdmmitagente.py${NC}"
echo ""
echo "4. Abre una SEGUNDA terminal."
echo "5. Activa el entorno virtual también en esta terminal: ${GREEN}${VENV_ACTIVATE_CMD}${NC}"
echo "6. Inicia la interfaz web ejecutando: ${GREEN}streamlit run streamlit_app.py${NC}"
echo ""
echo "Luego, abre tu navegador en la dirección que indique Streamlit (normalmente http://localhost:8501)."

#!/bin/bash
#
# Este script ejecuta las pruebas automatizadas para el proyecto JDMMitAgente.

# --- Configuración y Colores ---
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Detección del Entorno para encontrar el ejecutable de Python
OS="$(uname)"
PYTHON_CMD="python3"
VENV_PATH=".venv/bin/python"

if [[ "$OS" == "MINGW"* || "$OS" == "CYGWIN"* || "$OS" == "MSYS"* ]]; then
    PYTHON_CMD="python"
    VENV_PATH=".venv/Scripts/python"
fi

# --- Ejecución de las Pruebas --- #

echo -e "${YELLOW}Iniciando el conjunto de pruebas para JDMMitAgente...${NC}"

# 1. Verificar que el entorno virtual existe
if [ ! -d ".venv" ]; then
    echo -e "${RED}Error: El entorno virtual .venv no existe.${NC}"
    echo -e "Por favor, ejecuta primero el script 'install.sh' o 'scripts/setup-local.sh' para instalar las dependencias."
    exit 1
fi

# 2. Verificar que pytest está instalado
if ! $VENV_PATH -m pip show pytest &> /dev/null; then
    echo -e "${RED}Error: pytest no está instalado en el entorno virtual.${NC}"
    echo -e "Asegúrate de que el entorno está correctamente configurado."
    exit 1
fi

# 3. Ejecutar pytest
# -v: Modo verboso, muestra cada prueba que se ejecuta.
# -s: Muestra la salida (prints) de las pruebas, útil para depuración.
echo -e "${GREEN}Ejecutando pytest...${NC}"

$VENV_PATH -m pytest -v -s test_app.py

# Capturar el código de salida de pytest
EXIT_CODE=$?

# 4. Mostrar resultado final
if [ $EXIT_CODE -eq 0 ]; then
    echo -e "\n${GREEN}¡Todas las pruebas pasaron con éxito! ✅${NC}"
else
    echo -e "\n${RED}Algunas pruebas fallaron. ❌${NC}"
fi

exit $EXIT_CODE

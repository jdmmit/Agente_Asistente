#!/bin/bash
#
# Script principal de instalación y diagnóstico para Memorae.
# Ofrece la opción de instalar con Docker o localmente, y verifica la integridad de la instalación local.

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

# Detecta el comando de Python correcto (python3 o python)
detect_python_command() {
    if command -v python3 &> /dev/null; then
        PYTHON_CMD="python3"
    elif command -v python &> /dev/null; then
        PYTHON_CMD="python"
    else
        return 1
    fi
    return 0
}

# Comprueba los prerrequisitos para Docker
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

# Ejecuta el conjunto de pruebas y devuelve el resultado
run_tests() {
    echo -e "\n${CYAN}--- Ejecutando Pruebas Automatizadas ---${NC}"
    chmod +x run-tests.sh
    ./run-tests.sh
    return $?
}

# --- Lógica de Instalación Local ---

run_local_install() {
    echo -e "\n${YELLOW}Iniciando instalación local...${NC}"

    # 1. Verificar Python
    if ! detect_python_command; then
        echo -e "${RED}Error: No se encontró el comando 'python3' o 'python'.${NC}"
        echo "Por favor, instala Python 3.10+ y asegúrate de que esté en tu PATH."
        return 1
    fi
    echo -e "${GREEN}Python detectado: $($PYTHON_CMD --version)${NC}"

    # 2. Crear entorno virtual
    if [ ! -d "$VENV_DIR" ]; then
        echo -e "\nCreando entorno virtual en '$VENV_DIR'..."
        $PYTHON_CMD -m venv $VENV_DIR
    else
        echo -e "\nEl entorno virtual '$VENV_DIR' ya existe."
    fi

    # Activar entorno virtual (depende del SO)
VENV_PYTHON="$VENV_DIR/bin/python"
    if [[ "$OS" == "MINGW"* || "$OS" == "CYGWIN"* || "$OS" == "MSYS"* ]]; then
        VENV_PYTHON="$VENV_DIR/Scripts/python"
    fi

    # 3. Instalar/Actualizar dependencias
    echo -e "\nInstalando dependencias desde requirements.txt..."
    $VENV_PYTHON -m pip install --upgrade pip
    $VENV_PYTHON -m pip install -r requirements.txt
    if [ $? -ne 0 ]; then
        echo -e "${RED}Error durante la instalación de dependencias.${NC}"
        return 1
    fi

    # 4. Configurar el archivo .env
    if [ ! -f ".env" ]; then
        echo -e "\nCreando archivo de configuración .env..."
        echo "# Nombre de la base de datos local" > .env
        echo "DATABASE_NAME=memorae.db" >> .env
        echo "# URL de Ollama (si es diferente del valor por defecto)" >> .env
        echo "OLLAMA_HOST=http://localhost:11434" >> .env
        echo -e "${GREEN}Archivo .env creado con la configuración por defecto.${NC}"
    else
        echo -e "\nEl archivo .env ya existe."
    fi

    echo -e "${GREEN}Instalación local de dependencias completada.${NC}"
    
    # 5. Ejecutar pruebas
    run_tests
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}¡La instalación local ha sido verificada y funciona correctamente! ✅${NC}"
    else
        echo -e "${YELLOW}Las pruebas iniciales fallaron. Intentando reinstalar dependencias...${NC}"
        $VENV_PYTHON -m pip install --force-reinstall -r requirements.txt
        
        echo -e "\n${CYAN}--- Volviendo a Ejecutar las Pruebas ---${NC}"
        run_tests
        if [ $? -eq 0 ]; then
            echo -e "${GREEN}¡La reinstalación solucionó el problema! La instalación ha sido verificada. ✅${NC}"
        else
            echo -e "${RED}La auto-reparación falló. Las pruebas siguen sin pasar. ❌${NC}"
            echo -e "Posibles causas:
- El servicio de Ollama no está en ejecución.
- Hay un problema con la configuración del sistema (ej. drivers de audio).
- Revisa la salida de las pruebas para más detalles."
        fi
    fi
    return 0
}

# --- Menú Principal ---

show_main_menu() {
    echo -e "\n${CYAN}--- Instalador y Verificador de Memorae ---${NC}"
    echo -e "Elige una opción:"
    echo -e "1. ${GREEN}Instalar/Ejecutar con Docker (Recomendado)${NC}"
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
            echo -e "\nConstruyendo y levantando los contenedores... (Esto puede tardar)"
            
            if docker compose version &> /dev/null; then
                docker compose up --build
            else
                docker-compose up --build
            fi

            if [ $? -ne 0 ]; then
                echo -e "\n${RED}Error en Docker Compose.${NC}"
            fi
            echo -e "\nHas detenido los contenedores."
            ;;
        2)
            run_local_install
            echo -e "\nEl proceso de instalación/verificación local ha finalizado."
            break # Salir después de la instalación local
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

#!/bin/bash

# install.sh - Asistente de instalación y configuración para Memorae

# --- Colores para la salida ---
C_GREEN='\033[0;32m'
C_BLUE='\033[0;34m'
C_YELLOW='\033[1;33m'
C_RED='\033[0;31m'
C_NC='\033[0m' # No Color

# --- Funciones Auxiliares ---
print_header() {
    echo -e "${C_BLUE}==============================================${C_NC}"
    echo -e "${C_BLUE}    Asistente de Instalación de Memorae       ${C_NC}"
    echo -e "${C_BLUE}==============================================${C_NC}"
    echo
}

command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# --- Inicio del Script ---
clear
print_header

# --- 1. Verificación de Prerrequisitos ---
echo -e "${C_YELLOW}--- Paso 1: Verificando prerrequisitos ---${C_NC}"
if command_exists docker && command_exists ollama; then
    echo -e "✅ ${C_GREEN}Docker y Ollama están instalados.${C_NC}"
    echo "      Asegúrate de haber descargado un modelo (ej: ollama pull llama3)"
else
    echo -e "❌ ${C_RED}Error: Docker u Ollama no están instalados.${C_NC}"
    echo "Por favor, instálalos y vuelve a intentarlo."
    exit 1
fi
echo

# --- 2. Verificación del archivo .env ---
echo -e "${C_YELLOW}--- Paso 2: Verificando configuración de entorno ---${C_NC}"
if [ ! -f ".env" ]; then
    echo "No se encontró el archivo .env. Creando una plantilla..."
    bash utils/secure-env.sh
    echo
    echo -e "${C_YELLOW}---------------- ACCIÓN REQUERIDA ----------------${C_NC}"
    echo "He creado un archivo de plantilla llamado '.env.example'."
    echo
    echo "Por favor, sigue estos 3 pasos:
1. Renombra el archivo:   ${C_GREEN}mv .env.example .env${C_NC}
2. Ábrelo y edita los valores con tus credenciales.
3. Vuelve a ejecutar este instalador:   ${C_GREEN}bash install.sh${C_NC}"
    echo -e "${C_YELLOW}----------------------------------------------------${C_NC}"
    exit 0
else
    echo -e "✅ ${C_GREEN}¡Archivo .env encontrado!${C_NC}"
fi
echo

# --- 3. Instrucciones Finales de Arranque ---
echo -e "${C_YELLOW}--- Paso 3: ¡Listo para arrancar! ---${C_NC}"

# Dar permisos de ejecución a los scripts de inicio
chmod +x start-modern.sh
chmod +x start-legacy.sh

echo "Tu entorno está completamente configurado."
echo "Ahora puedes iniciar la aplicación usando uno de los siguientes comandos:"
echo

echo -e "Opción 1: Para versiones ${C_GREEN}NUEVAS${C_NC} de Docker (intenta esta primero)"
_cmd="bash start-modern.sh"
echo "  $_cmd"
echo

echo -e "Opción 2: Si la opción 1 falla, para versiones ${C_YELLOW}ANTIGUAS${C_NC} de Docker"
_cmd="bash start-legacy.sh"
echo "  $_cmd"
echo

echo "La aplicación puede tardar un minuto en iniciarse la primera vez."
echo -e "Una vez iniciada, accede a ella en ${C_BLUE}http://localhost:8501${C_NC}"

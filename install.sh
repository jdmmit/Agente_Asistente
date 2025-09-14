#!/bin/bash

# install.sh - Asistente de instalación y configuración para Memorae

# --- Colores para la salida ---
C_GREEN='\033[0;32m'
C_BLUE='\033[0;34m'
C_YELLOW='\033[1;33m'
C_RED='\033[0;31m'
C_NC='\033[0m' # No Color

# --- Funciones Auxiliares ---

# Función para imprimir un encabezado
print_header() {
    echo -e "${C_BLUE}==============================================${C_NC}"
    echo -e "${C_BLUE}    Asistente de Instalación de Memorae       ${C_NC}"
    echo -e "${C_BLUE}==============================================${C_NC}"
    echo
}

# Función para comprobar si un comando existe
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# --- Inicio del Script ---

clear
print_header

echo "Este script te guiará a través de la instalación de Memorae."
echo "Se comprobarán los prerrequisitos y se iniciará la aplicación con Docker."
echo

# --- 1. Verificación de Prerrequisitos ---
echo -e "${C_YELLOW}--- Paso 1: Verificando prerrequisitos ---${C_NC}"

# Comprobar Docker
if command_exists docker; then
    echo -e "✅ ${C_GREEN}Docker está instalado.${C_NC}"
else
    echo -e "❌ ${C_RED}Error: Docker no está instalado.${C_NC}"
    echo "Por favor, instálalo desde: https://docs.docker.com/get-docker/"
    exit 1
fi

# Comprobar Ollama
if command_exists ollama; then
    echo -e "✅ ${C_GREEN}Ollama está instalado.${C_NC}"
    echo "Asegúrate de haber descargado un modelo (ej: ollama pull llama3)"
else
    echo -e "❌ ${C_RED}Error: Ollama no está instalado.${C_NC}"
    echo "Por favor, instálalo desde: https://ollama.com/download"
    exit 1
fi

echo
echo -e "${C_GREEN}¡Genial! Todos los prerrequisitos están cumplidos.${C_NC}"
echo

# --- 2. Iniciar el Entorno de Docker ---
echo -e "${C_YELLOW}--- Paso 2: Configurando e iniciando el entorno ---${C_NC}"
echo "A continuación, se configurará tu entorno (si es la primera vez) y se iniciarán los servicios de Docker."
echo

# Dar permisos de ejecución al script de Docker y ejecutarlo
if [ -f "run-docker.sh" ]; then
    chmod +x run-docker.sh
    ./run-docker.sh
else
    echo -e "${C_RED}Error: El script 'run-docker.sh' no se encontró. Abortando.${C_NC}"
    exit 1
fi

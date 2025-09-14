#!/bin/bash

# secure-env.sh - Asistente interactivo para crear el archivo .env

# --- Colores para la salida ---
C_GREEN='\033[0;32m'
C_BLUE='\033[0;34m'
C_YELLOW='\033[1;33m'
C_NC='\033[0m' # No Color

# --- Funciones de Entrada ---

# Función para requerir una entrada del usuario. No puede estar vacía.
# Lee directamente de la terminal (/dev/tty) para evitar interferencias
# de herramientas externas como Firebase CLI.
require_input() {
    local prompt_text="$1"
    local input
    while true; do
        read -p "$prompt_text: " input </dev/tty
        if [[ -n "$input" ]]; then
            echo "$input"
            break
        fi
    done
}

# Función para pedir una entrada opcional con un valor por defecto.
# También lee directamente de /dev/tty.
prompt() {
    local prompt_text="$1"
    local input
    read -p "$prompt_text: " input </dev/tty
    echo "$input"
}

# --- Inicio del Script ---
echo -e "${C_BLUE}-------------------------------------${C_NC}"
echo -e "${C_BLUE} Memorae Environment Setup${C_NC}"
echo -e "${C_BLUE}-------------------------------------${C_NC}"
echo "This script will help you create a secure .env file for your assistant."
echo "You can press Enter to accept the default values in brackets [like this]."
echo ""

# --- Recopilación de Datos ---

# Get user name (optional, with default)
user_name=$(prompt "Enter your name [User]")

# Get email credentials (required)
email_user=$(require_input "Enter your Gmail address (for sending notifications)")
email_pass=$(require_input "Enter your Gmail App Password (search Google for 'Gmail App Password')")

# Get WhatsApp number (optional)
whatsapp_number=$(prompt "Enter your WhatsApp number (e.g., +11234567890)")

# Get Ollama model (optional, with default)
ollama_model=$(prompt "Enter the Ollama model to use [llama3]")

# --- Generación del Archivo ---

# Establecer valores por defecto si están vacíos
: "${user_name:=User}"
: "${ollama_model:=llama3}"

# Crear contenido del archivo .env
ENV_CONTENT="# .env - Secure environment variables for Memorae

# -- User Information --
USER_NAME=\"${user_name}\"

# -- Email Configuration (for sending notifications) --
EMAIL_USER=\"${email_user}\"
EMAIL_PASS=\"${email_pass}\"

# -- WhatsApp Configuration --
# Your full number, including country code (e.g., +11234567890)
WHATSAPP_NUMBER=\"${whatsapp_number}\"

# -- Ollama LLM Configuration --
# The model to use for generating responses (e.g., llama3, phi3)
OLLAMA_MODEL=\"${ollama_model}\"

# -- Ollama Connection --
# For local setup, Ollama runs on the host machine.
# For Docker, this will be automatically overridden.
OLLAMA_HOST=http://127.0.0.1:11434
"

# Escribir el archivo .env
if echo -e "$ENV_CONTENT" > .env; then
    echo ""
    echo -e "✅ ${C_GREEN}Success! Your .env file has been created.${C_NC}"
    echo "The application will now start..."
else
    echo ""
    echo -e "❌ ${C_RED}Error! Could not create the .env file.${C_NC}"
    echo "Please check your permissions and try again."
fi

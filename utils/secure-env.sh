#!/bin/bash

# secure-env.sh - Crea una plantilla .env.example con instrucciones.

# --- Colores para la salida ---
C_GREEN='\033[0;32m'
C_YELLOW='\033[1;33m'
C_RED='\033[0;31m'
C_NC='\033[0m' # No Color

echo -e "${C_YELLOW}Creando archivo de plantilla de entorno...${C_NC}"

# --- Generación del Archivo Plantilla---
TEMPLATE_CONTENT="# .env - Variables de entorno seguras para Memorae
#
# INSTRUCCIONES:
# 1. RENOMBRA este archivo de '.env.example' a '.env'
# 2. RELLENA los valores de abajo. No dejes vacíos los valores requeridos.
# 3. GUARDA el archivo.
#
# NOTA: Este archivo .env es ignorado por Git, por lo que tus secretos están a salvo.

# -- Información de Usuario --
USER_NAME=\"User\"

# -- Configuración de Email (REQUERIDO para enviar notificaciones) --
EMAIL_USER=\"tu_email@gmail.com\"
EMAIL_PASS=\"tu_contraseña_de_aplicacion_de_16_digitos_de_gmail\"

# -- Configuración de WhatsApp (OPCIONAL) --
# Tu número completo, incluyendo código de país (ej: +11234567890)
WHATSAPP_NUMBER=\"\"

# -- Configuración de LLM Ollama --
# El modelo a usar para generar respuestas
OLLAMA_MODEL=\"llama3\"

# -- Conexión con Ollama --
# Para configuración local, Ollama se ejecuta en la máquina anfitriona.
# Esto es sobreescrito por Docker Compose para la comunicación entre contenedores.
OLLAMA_HOST=http://127.0.0.1:11434
"

# Escribir el archivo .env.example
if echo -e "$TEMPLATE_CONTENT" > .env.example; then
    echo -e "✅ ${C_GREEN}¡Éxito! Se ha creado '.env.example'.${C_NC}"
else
    echo -e "❌ ${C_RED}¡Error! No se pudo crear el archivo .env.example.${C_NC}"
fi

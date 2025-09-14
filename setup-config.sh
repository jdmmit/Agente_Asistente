#!/bin/bash
# JDMMitAgente - Configurador Simplificado

set -e
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
WHITE='\033[1;37m'
NC='\033[0m'

echo -e "${WHITE}🤖 JDMMitAgente - Configurador${NC}"
echo "=================================="

echo -ne "${YELLOW}Tu nombre completo: ${NC}"
read OWNER_NAME

echo -ne "${YELLOW}Nombre del asistente [JDMMitAgente]: ${NC}"
read ASSISTANT_NAME
ASSISTANT_NAME=${ASSISTANT_NAME:-JDMMitAgente}

echo ""
echo -ne "${YELLOW}Tu email: ${NC}"
read EMAIL_USER

echo -ne "${YELLOW}Contraseña del email: ${NC}"
read -s EMAIL_PASS
echo ""

echo -ne "${YELLOW}¿WhatsApp? (s/n): ${NC}"
read use_whatsapp
if [[ $use_whatsapp =~ ^[SsYy]$ ]]; then
    echo -ne "${YELLOW}Número WhatsApp (+1234567890): ${NC}"
    read WHATSAPP_NUMBER
else
    WHATSAPP_NUMBER=""
fi

# Generar contraseña de BD
if command -v openssl &> /dev/null; then
    DB_PASSWORD=$(openssl rand -base64 12 | tr -d "=+/")
else
    DB_PASSWORD=$(date +%s | sha256sum | head -c 12)
fi

# Crear backup si existe .env
if [ -f ".env" ]; then
    cp .env .env.backup.$(date +%Y%m%d_%H%M%S)
fi

# Generar archivo .env
cat > .env << 'ENVFILE'
OWNER_NAME='${OWNER_NAME}'
ASSISTANT_NAME='${ASSISTANT_NAME}'
MODEL='llama3.2'
DB_TYPE='mysql'
DB_HOST='mysql'
DB_PORT='3306'
DB_USER='jdmmit_user'
DB_PASSWORD='${DB_PASSWORD}'
DB_NAME='jdmmitagente_db'
EMAIL_SMTP='smtp.gmail.com'
EMAIL_PORT='587'
EMAIL_USER='${EMAIL_USER}'
EMAIL_PASS='${EMAIL_PASS}'
WHATSAPP_NUMBER='${WHATSAPP_NUMBER}'
GOOGLE_SPEECH_LANGUAGE='es-ES'
LOG_FILE='jdmmitagente.log'
OLLAMA_HOST='http://ollama:11434'
CONFIG_VERSION='3.0.0'
CONFIG_DATE='$(date -I)'
ENVFILE

# Sustituir variables usando Python (seguro para todos caracteres especiales)
python3 -c "
import os
env_file = '.env'
lines = []
with open(env_file, 'r') as f:
    lines = f.readlines()

new_lines = []
for line in lines:
    line = line.rstrip()
    if line.startswith('OWNER_NAME='):
        new_lines.append('OWNER_NAME=\"$OWNER_NAME\"')
    elif line.startswith('ASSISTANT_NAME='):
        new_lines.append('ASSISTANT_NAME=\"$ASSISTANT_NAME\"')
    elif line.startswith('EMAIL_USER='):
        new_lines.append('EMAIL_USER=\"$EMAIL_USER\"')
    elif line.startswith('EMAIL_PASS='):
        new_lines.append('EMAIL_PASS=\"$EMAIL_PASS\"')
    elif line.startswith('WHATSAPP_NUMBER='):
        new_lines.append('WHATSAPP_NUMBER=\"$WHATSAPP_NUMBER\"')
    elif line.startswith('DB_PASSWORD='):
        new_lines.append('DB_PASSWORD=\"$DB_PASSWORD\"')
    elif line.startswith('CONFIG_DATE='):
        new_lines.append('CONFIG_DATE=\"$(date -I)\"')
    else:
        new_lines.append(line)
    new_lines.append('\\n')

with open(env_file, 'w') as f:
    f.writelines(new_lines)
print('✅ Variables sustituidas en .env sin errores')
"
OWNER_NAME="$OWNER_NAME" ASSISTANT_NAME="$ASSISTANT_NAME" EMAIL_USER="$EMAIL_USER" EMAIL_PASS="$EMAIL_PASS" WHATSAPP_NUMBER="$WHATSAPP_NUMBER" DB_PASSWORD="$DB_PASSWORD"

chmod 600 .env

echo ""
echo -e "${GREEN}✅ Configuración guardada en .env${NC}"
echo -e "${WHITE}Próximos pasos:${NC}"
echo "1. ./install.sh"
echo "2. ./run-docker.sh"

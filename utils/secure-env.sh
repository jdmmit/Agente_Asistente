#!/bin/bash

# Utilidad de Seguridad para JDMMitAgente
set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
WHITE='\033[1;37m'
NC='\033[0m'

ENV_FILE=".env"
ENCRYPTED_FILE=".env.encrypted"
KEY_FILE=".env.key"

show_help() {
    echo -e "${WHITE}🔐 JDMMitAgente - Utilidad de Seguridad${NC}"
    echo ""
    echo "Uso: ./utils/secure-env.sh [comando]"
    echo ""
    echo "Comandos:"
    echo "  encrypt    Encriptar archivo .env"
    echo "  decrypt    Desencriptar archivo .env"
    echo "  backup     Crear backup encriptado"
    echo "  check      Verificar integridad"
    echo "  --help     Mostrar esta ayuda"
}

encrypt_env() {
    if [ ! -f "$ENV_FILE" ]; then
        echo -e "${RED}❌ No se encontró $ENV_FILE${NC}"
        exit 1
    fi
    
    if ! command -v openssl &> /dev/null; then
        echo -e "${RED}❌ OpenSSL no encontrado${NC}"
        exit 1
    fi
    
    echo -e "${GREEN}🔐 Encriptando configuración...${NC}"
    
    # Generar clave si no existe
    if [ ! -f "$KEY_FILE" ]; then
        openssl rand -base64 32 > "$KEY_FILE"
        chmod 600 "$KEY_FILE"
    fi
    
    # Encriptar
    openssl enc -aes-256-cbc -salt -in "$ENV_FILE" -out "$ENCRYPTED_FILE" -pass file:"$KEY_FILE"
    
    echo -e "${GREEN}✅ Archivo encriptado: $ENCRYPTED_FILE${NC}"
}

decrypt_env() {
    if [ ! -f "$ENCRYPTED_FILE" ] || [ ! -f "$KEY_FILE" ]; then
        echo -e "${RED}❌ Archivos de encriptación no encontrados${NC}"
        exit 1
    fi
    
    openssl enc -aes-256-cbc -d -salt -in "$ENCRYPTED_FILE" -out "$ENV_FILE" -pass file:"$KEY_FILE"
    chmod 600 "$ENV_FILE"
    echo -e "${GREEN}✅ Archivo desencriptado${NC}"
}

backup_env() {
    if [ ! -f "$ENV_FILE" ]; then
        echo -e "${RED}❌ No se encontró $ENV_FILE${NC}"
        exit 1
    fi
    
    backup_file="env_backup_$(date +%Y%m%d_%H%M%S).tar.gz"
    tar -czf "$backup_file" "$ENV_FILE"
    echo -e "${GREEN}✅ Backup creado: $backup_file${NC}"
}

check_integrity() {
    echo -e "${WHITE}🔍 Verificando integridad...${NC}"
    
    if [ -f "$ENV_FILE" ]; then
        echo -e "${GREEN}✅ $ENV_FILE encontrado${NC}"
        if [ "$(stat -c %a "$ENV_FILE")" = "600" ]; then
            echo -e "${GREEN}✅ Permisos correctos (600)${NC}"
        else
            echo -e "${YELLOW}⚠️  Permisos incorrectos${NC}"
            chmod 600 "$ENV_FILE"
            echo -e "${GREEN}🔧 Permisos corregidos${NC}"
        fi
    else
        echo -e "${RED}❌ $ENV_FILE no encontrado${NC}"
    fi
    
    if [ -f "$KEY_FILE" ]; then
        echo -e "${GREEN}✅ Clave de encriptación encontrada${NC}"
    fi
}

case "${1:-}" in
    encrypt) encrypt_env ;;
    decrypt) decrypt_env ;;
    backup) backup_env ;;
    check) check_integrity ;;
    --help|-h|help|*) show_help ;;
esac

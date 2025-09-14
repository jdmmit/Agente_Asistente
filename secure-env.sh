#!/bin/bash

# Utilidad de Seguridad para JDMMitAgente
# Encriptar y desencriptar datos sensibles en .env

set -e

# Colores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
WHITE='\033[1;37m'
NC='\033[0m'

# Archivo de configuración
ENV_FILE=".env"
ENCRYPTED_FILE=".env.encrypted"
KEY_FILE=".env.key"

# Función para mostrar ayuda
show_help() {
    echo -e "${WHITE}🔐 JDMMitAgente - Utilidad de Seguridad${NC}"
    echo ""
    echo -e "${YELLOW}Uso:${NC}"
    echo "  ./secure-env.sh encrypt    # Encriptar .env"
    echo "  ./secure-env.sh decrypt    # Desencriptar .env" 
    echo "  ./secure-env.sh backup     # Crear backup encriptado"
    echo "  ./secure-env.sh restore    # Restaurar desde backup"
    echo "  ./secure-env.sh check      # Verificar integridad"
    echo "  ./secure-env.sh --help     # Mostrar esta ayuda"
    echo ""
    echo -e "${YELLOW}Descripción:${NC}"
    echo "  Esta utilidad te permite encriptar los datos sensibles"
    echo "  de tu configuración para almacenamiento seguro."
    echo ""
}

# Generar clave de encriptación
generate_key() {
    if [ ! -f "$KEY_FILE" ]; then
        echo -e "${BLUE}🔑 Generando clave de encriptación...${NC}"
        openssl rand -base64 32 > "$KEY_FILE"
        chmod 600 "$KEY_FILE"
        echo -e "${GREEN}✅ Clave generada en $KEY_FILE${NC}"
    fi
}

# Encriptar archivo .env
encrypt_env() {
    if [ ! -f "$ENV_FILE" ]; then
        echo -e "${RED}❌ No se encontró $ENV_FILE${NC}"
        exit 1
    fi
    
    generate_key
    
    echo -e "${BLUE}🔐 Encriptando configuración...${NC}"
    
    # Crear backup no encriptado
    cp "$ENV_FILE" "${ENV_FILE}.backup.$(date +%Y%m%d_%H%M%S)"
    
    # Encriptar
    openssl enc -aes-256-cbc -salt -in "$ENV_FILE" -out "$ENCRYPTED_FILE" -pass file:"$KEY_FILE"
    
    # Verificar
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ Configuración encriptada exitosamente${NC}"
        echo -e "${YELLOW}📄 Archivo encriptado: $ENCRYPTED_FILE${NC}"
        echo -e "${YELLOW}🔑 Clave de encriptación: $KEY_FILE${NC}"
        echo ""
        echo -e "${WHITE}⚠️  IMPORTANTE:${NC}"
        echo -e "${YELLOW}   - Guarda $KEY_FILE en un lugar seguro${NC}"
        echo -e "${YELLOW}   - Sin la clave no podrás desencriptar los datos${NC}"
        echo -e "${YELLOW}   - Considera usar un gestor de contraseñas${NC}"
        
        # Preguntar si eliminar .env original
        echo ""
        read -p "$(echo -e ${YELLOW}¿Eliminar $ENV_FILE original? (s/n): ${NC})" remove_original
        if [[ $remove_original =~ ^[SsYy]$ ]]; then
            rm "$ENV_FILE"
            echo -e "${GREEN}✅ Archivo original eliminado${NC}"
        fi
        
    else
        echo -e "${RED}❌ Error durante la encriptación${NC}"
        exit 1
    fi
}

# Desencriptar archivo .env
decrypt_env() {
    if [ ! -f "$ENCRYPTED_FILE" ]; then
        echo -e "${RED}❌ No se encontró $ENCRYPTED_FILE${NC}"
        exit 1
    fi
    
    if [ ! -f "$KEY_FILE" ]; then
        echo -e "${RED}❌ No se encontró la clave de encriptación $KEY_FILE${NC}"
        exit 1
    fi
    
    echo -e "${BLUE}🔓 Desencriptando configuración...${NC}"
    
    # Desencriptar
    openssl enc -aes-256-cbc -d -salt -in "$ENCRYPTED_FILE" -out "$ENV_FILE" -pass file:"$KEY_FILE"
    
    # Verificar
    if [ $? -eq 0 ]; then
        chmod 600 "$ENV_FILE"
        echo -e "${GREEN}✅ Configuración desencriptada exitosamente${NC}"
        echo -e "${YELLOW}📄 Archivo restaurado: $ENV_FILE${NC}"
    else
        echo -e "${RED}❌ Error durante la desencriptación${NC}"
        echo -e "${YELLOW}Verifica que la clave de encriptación sea correcta${NC}"
        exit 1
    fi
}

# Crear backup encriptado
backup_env() {
    if [ ! -f "$ENV_FILE" ]; then
        echo -e "${RED}❌ No se encontró $ENV_FILE${NC}"
        exit 1
    fi
    
    generate_key
    
    local backup_file="env_backup_$(date +%Y%m%d_%H%M%S).encrypted"
    
    echo -e "${BLUE}💾 Creando backup encriptado...${NC}"
    
    openssl enc -aes-256-cbc -salt -in "$ENV_FILE" -out "$backup_file" -pass file:"$KEY_FILE"
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ Backup encriptado creado: $backup_file${NC}"
    else
        echo -e "${RED}❌ Error creando backup${NC}"
        exit 1
    fi
}

# Restaurar desde backup
restore_env() {
    echo -e "${BLUE}📋 Backups encriptados disponibles:${NC}"
    ls -la env_backup_*.encrypted 2>/dev/null || {
        echo -e "${YELLOW}⚠️  No se encontraron backups encriptados${NC}"
        exit 1
    }
    
    echo ""
    read -p "$(echo -e ${YELLOW}Nombre del backup a restaurar: ${NC})" backup_name
    
    if [ ! -f "$backup_name" ]; then
        echo -e "${RED}❌ Backup no encontrado: $backup_name${NC}"
        exit 1
    fi
    
    if [ ! -f "$KEY_FILE" ]; then
        echo -e "${RED}❌ Clave de encriptación no encontrada${NC}"
        exit 1
    fi
    
    # Crear backup del .env actual si existe
    if [ -f "$ENV_FILE" ]; then
        cp "$ENV_FILE" "${ENV_FILE}.pre_restore.$(date +%Y%m%d_%H%M%S)"
        echo -e "${YELLOW}📄 Backup del archivo actual creado${NC}"
    fi
    
    echo -e "${BLUE}🔄 Restaurando desde backup...${NC}"
    
    openssl enc -aes-256-cbc -d -salt -in "$backup_name" -out "$ENV_FILE" -pass file:"$KEY_FILE"
    
    if [ $? -eq 0 ]; then
        chmod 600 "$ENV_FILE"
        echo -e "${GREEN}✅ Configuración restaurada desde $backup_name${NC}"
    else
        echo -e "${RED}❌ Error restaurando backup${NC}"
        exit 1
    fi
}

# Verificar integridad
check_integrity() {
    echo -e "${BLUE}🔍 Verificando integridad de archivos...${NC}"
    
    local issues=0
    
    # Verificar .env
    if [ -f "$ENV_FILE" ]; then
        if [ "$(stat -c %a "$ENV_FILE")" = "600" ]; then
            echo -e "${GREEN}✅ $ENV_FILE - permisos correctos (600)${NC}"
        else
            echo -e "${YELLOW}⚠️  $ENV_FILE - permisos incorrectos$(NC}"
            ((issues++))
        fi
        
        # Verificar que no contenga datos de ejemplo
        if grep -q "tu_email@gmail.com" "$ENV_FILE" 2>/dev/null; then
            echo -e "${YELLOW}⚠️  $ENV_FILE - contiene datos de ejemplo${NC}"
            ((issues++))
        fi
        
        if grep -q "tu_app_password" "$ENV_FILE" 2>/dev/null; then
            echo -e "${YELLOW}⚠️  $ENV_FILE - contiene contraseñas de ejemplo${NC}"
            ((issues++))
        fi
    else
        echo -e "${RED}❌ $ENV_FILE no encontrado${NC}"
        ((issues++))
    fi
    
    # Verificar clave de encriptación
    if [ -f "$KEY_FILE" ]; then
        if [ "$(stat -c %a "$KEY_FILE")" = "600" ]; then
            echo -e "${GREEN}✅ $KEY_FILE - permisos correctos (600)${NC}"
        else
            echo -e "${YELLOW}⚠️  $KEY_FILE - permisos incorrectos${NC}"
            chmod 600 "$KEY_FILE"
            echo -e "${GREEN}🔧 Permisos corregidos${NC}"
        fi
    fi
    
    # Verificar archivo encriptado
    if [ -f "$ENCRYPTED_FILE" ]; then
        echo -e "${GREEN}✅ $ENCRYPTED_FILE encontrado${NC}"
    fi
    
    echo ""
    if [ $issues -eq 0 ]; then
        echo -e "${GREEN}🎉 Verificación completa - sin problemas${NC}"
    else
        echo -e "${YELLOW}⚠️  Se encontraron $issues problema(s)${NC}"
        echo -e "${YELLOW}Considera ejecutar ./setup-config.sh para reconfigurar${NC}"
    fi
}

# Función principal
main() {
    case "${1:-}" in
        encrypt)
            encrypt_env
            ;;
        decrypt)
            decrypt_env
            ;;
        backup)
            backup_env
            ;;
        restore)
            restore_env
            ;;
        check)
            check_integrity
            ;;
        --help|-h|help)
            show_help
            ;;
        *)
            echo -e "${RED}❌ Comando inválido: ${1:-}${NC}"
            echo ""
            show_help
            exit 1
            ;;
    esac
}

# Verificar dependencias
if ! command -v openssl &> /dev/null; then
    echo -e "${RED}❌ OpenSSL no está instalado${NC}"
    echo "Instálalo con: sudo apt-get install openssl"
    exit 1
fi

# Ejecutar función principal
main "$@"

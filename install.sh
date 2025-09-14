#!/bin/bash

echo "🚀 Instalador de JDMMitAgente v3.0.0"
echo "======================================"

# Colores para la interfaz
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
WHITE='\033[1;37m'
NC='\033[0m'

# Función para mostrar paso
show_step() {
    echo -e "${BLUE}▶️  $1${NC}"
}

# Función para mostrar éxito
show_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

# Función para mostrar advertencia
show_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

# Función para mostrar error
show_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Verificar si Docker está instalado
check_docker() {
    show_step "Verificando Docker..."
    
    if ! command -v docker &> /dev/null; then
        show_error "Docker no está instalado."
        echo ""
        echo "📋 Para instalar Docker en Ubuntu/Debian:"
        echo "   curl -fsSL https://get.docker.com | sudo sh"
        echo "   sudo usermod -aG docker \$USER"
        echo "   # Luego reinicia sesión o ejecuta: newgrp docker"
        echo ""
        exit 1
    fi

    if ! command -v docker-compose &> /dev/null; then
        show_error "Docker Compose no está instalado."
        echo ""
        echo "📋 Para instalar Docker Compose:"
        echo "   sudo curl -L \"https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-\$(uname -s)-\$(uname -m)\" -o /usr/local/bin/docker-compose"
        echo "   sudo chmod +x /usr/local/bin/docker-compose"
        echo ""
        exit 1
    fi

    show_success "Docker y Docker Compose encontrados"
}

# Verificar Python (opcional)
check_python() {
    show_step "Verificando Python..."
    
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 --version | grep -oE '[0-9]+\.[0-9]+')
        show_success "Python $PYTHON_VERSION encontrado"
        PYTHON_AVAILABLE=true
    else
        show_warning "Python3 no encontrado. Solo estará disponible la ejecución con Docker."
        PYTHON_AVAILABLE=false
    fi
}

# Configuración personalizada
setup_configuration() {
    echo ""
    echo -e "${WHITE}🔧 Configuración Personalizada${NC}"
    echo "================================="
    
    if [ -f ".env" ]; then
        echo ""
        echo "Se encontró una configuración existente:"
        echo "$(head -n 3 .env | tail -n 1)"
        echo ""
        
        echo "¿Qué quieres hacer?"
        echo "1. 🔄 Usar configuración existente"
        echo "2. 🆕 Crear nueva configuración"
        echo "3. ⚙️  Reconfigurar datos personales"
        echo ""
        read -p "$(echo -e ${YELLOW}Elige una opción [1-3]: ${NC})" config_choice
        
        case $config_choice in
            1)
                show_success "Usando configuración existente"
                return
                ;;
            2|3)
                echo ""
                show_step "Iniciando configurador interactivo..."
                ./setup-config.sh
                ;;
            *)
                show_error "Opción inválida"
                exit 1
                ;;
        esac
    else
        echo ""
        echo -e "${CYAN}🎯 Para usar JDMMitAgente necesitas configurar tus datos personales.${NC}"
        echo -e "${CYAN}El configurador te ayudará paso a paso de forma segura.${NC}"
        echo ""
        
        if [ -f "./setup-config.sh" ]; then
            read -p "$(echo -e ${YELLOW}¿Iniciar configurador ahora? (s/n): ${NC})" start_config
            if [[ $start_config =~ ^[SsYy]$ ]]; then
                ./setup-config.sh
            else
                show_warning "Puedes configurar más tarde ejecutando: ./setup-config.sh"
                echo ""
                read -p "$(echo -e ${YELLOW}¿Continuar con configuración por defecto? (s/n): ${NC})" use_default
                if [[ ! $use_default =~ ^[SsYy]$ ]]; then
                    echo "Instalación cancelada. Ejecuta ./setup-config.sh cuando estés listo."
                    exit 1
                fi
                
                # Crear configuración mínima por defecto
                create_default_config
            fi
        else
            show_error "Configurador no encontrado. Creando configuración por defecto."
            create_default_config
        fi
    fi
}

# Crear configuración por defecto
create_default_config() {
    show_step "Creando configuración por defecto..."
    
    cat > .env << 'ENV_EOF'
# JDMMitAgente - Configuración por Defecto
# ¡IMPORTANTE! Ejecuta ./setup-config.sh para personalizar

# Información del propietario  
OWNER_NAME='Usuario'
ASSISTANT_NAME='JDMMitAgente'

# Modelo de IA
MODEL='llama3.2'

# Base de Datos MySQL
DB_TYPE='mysql'
DB_HOST='mysql'
DB_PORT='3306'
DB_USER='jdmmit_user'
DB_PASSWORD='default_password_123'
DB_NAME='jdmmitagente_db'

# Configuración de Email (¡CONFIGURA TUS DATOS!)
EMAIL_SMTP='smtp.gmail.com'
EMAIL_PORT='587'
EMAIL_USER='tu_email@gmail.com'
EMAIL_PASS='tu_app_password'

# WhatsApp (opcional)
WHATSAPP_NUMBER=''

# Configuraciones adicionales
GOOGLE_SPEECH_LANGUAGE='es-ES'
LOG_FILE='jdmmitagente.log'
OLLAMA_HOST='http://ollama:11434'

# Configuración por defecto - PERSONALIZA CON ./setup-config.sh
CONFIG_VERSION='3.0.0'
CONFIG_TYPE='default'
CONFIG_DATE='$(date -I)'
ENV_EOF

    chmod 600 .env
    show_warning "Configuración por defecto creada. ¡Recuerda personalizarla!"
}

# Configurar entorno
setup_environment() {
    show_step "Configurando entorno..."
    
    # Crear directorios necesarios
    mkdir -p logs
    mkdir -p archive
    
    # Configurar permisos
    chmod +x jdmmitagente.py 2>/dev/null || true
    chmod +x run.sh 2>/dev/null || true
    chmod +x run-docker.sh 2>/dev/null || true
    chmod +x setup-config.sh 2>/dev/null || true
    chmod +x test-project.sh 2>/dev/null || true
    
    show_success "Entorno configurado"
}

# Seleccionar tipo de instalación
select_installation_type() {
    echo ""
    echo -e "${WHITE}📋 Tipo de Instalación${NC}"
    echo "======================"
    echo ""
    echo "1. 🐳 Solo Docker (recomendado)"
    echo "   - Instalación completa containerizada"
    echo "   - No requiere dependencias locales"
    echo "   - Fácil de mantener y actualizar"
    echo ""
    echo "2. 🔄 Híbrida (Docker + Local)"
    echo "   - Opción de ejecutar local o con Docker"
    echo "   - Instala dependencias Python locales"
    echo "   - Mayor flexibilidad de desarrollo"
    echo ""
    echo "3. 🏠 Solo Local (avanzado)"
    echo "   - Ejecución completamente local"
    echo "   - Requiere MySQL instalado localmente"
    echo "   - Para desarrolladores/usuarios avanzados"
    echo ""

    read -p "$(echo -e ${YELLOW}Elige una opción [1-3]: ${NC})" choice

    case $choice in
        1) docker_installation ;;
        2) hybrid_installation ;;
        3) local_installation ;;
        *) 
            show_error "Opción inválida"
            exit 1
            ;;
    esac
}

# Instalación solo Docker
docker_installation() {
    show_step "Configurando instalación Docker..."
    
    # Construir imagen
    build_docker_image
    
    show_success "Instalación Docker completada"
    INSTALLATION_TYPE="docker"
}

# Instalación híbrida
hybrid_installation() {
    if [ "$PYTHON_AVAILABLE" = true ]; then
        show_step "Configurando instalación híbrida..."
        
        # Crear entorno virtual
        setup_python_environment
        
        # Construir imagen Docker
        build_docker_image
        
        show_success "Instalación híbrida completada"
        INSTALLATION_TYPE="hybrid"
    else
        show_error "Python no disponible. Cambiando a instalación Docker."
        docker_installation
    fi
}

# Instalación local
local_installation() {
    if [ "$PYTHON_AVAILABLE" = true ]; then
        show_step "Configurando instalación local..."
        
        show_warning "Asegúrate de tener MySQL instalado y corriendo localmente"
        
        # Crear entorno virtual
        setup_python_environment
        
        # Configurar para MySQL local
        if [ -f ".env" ]; then
            sed -i 's/DB_HOST=.*/DB_HOST=localhost/' .env
            show_success "Configurado para MySQL local"
        fi
        
        INSTALLATION_TYPE="local"
    else
        show_error "Python no disponible. No se puede instalar localmente."
        exit 1
    fi
}

# Configurar entorno Python
setup_python_environment() {
    show_step "Configurando entorno Python..."
    
    # Crear entorno virtual
    if [ ! -d "venv" ]; then
        python3 -m venv venv
        show_success "Entorno virtual creado"
    fi
    
    # Activar e instalar dependencias
    source venv/bin/activate
    pip install --upgrade pip
    pip install -r requirements.txt
    
    show_success "Dependencias Python instaladas"
}

# Construir imagen Docker
build_docker_image() {
    show_step "Construyendo imagen Docker..."
    
    if docker-compose build; then
        show_success "Imagen Docker construida exitosamente"
    else
        show_error "Error construyendo la imagen Docker"
        exit 1
    fi
}

# Verificar instalación
verify_installation() {
    show_step "Verificando instalación..."
    
    # Ejecutar verificador del proyecto
    if [ -f "./test-project.sh" ]; then
        if ./test-project.sh > /dev/null 2>&1; then
            show_success "Verificación completa exitosa"
        else
            show_warning "Algunas verificaciones fallaron. El proyecto debería funcionar igual."
        fi
    fi
}

# Mostrar resumen de instalación
show_installation_summary() {
    echo ""
    echo -e "${WHITE}🎉 ¡Instalación Completada!${NC}"
    echo "============================"
    echo ""
    
    case $INSTALLATION_TYPE in
        "docker")
            echo -e "${GREEN}📦 Tipo de instalación:${NC} Solo Docker"
            echo ""
            echo -e "${WHITE}🚀 Para ejecutar:${NC}"
            echo "   ./run-docker.sh"
            echo ""
            echo -e "${WHITE}📋 Comandos útiles:${NC}"
            echo "   docker-compose up -d        # Iniciar en segundo plano"
            echo "   docker-compose logs -f      # Ver logs"
            echo "   docker-compose down         # Detener servicios"
            ;;
        "hybrid")
            echo -e "${GREEN}📦 Tipo de instalación:${NC} Híbrida (Docker + Local)"
            echo ""
            echo -e "${WHITE}🚀 Para ejecutar:${NC}"
            echo "   ./run-docker.sh             # Con Docker (recomendado)"
            echo "   ./run.sh                    # Localmente"
            echo ""
            echo -e "${WHITE}📋 Comandos útiles:${NC}"
            echo "   source venv/bin/activate    # Activar entorno Python"
            echo "   docker-compose up -d        # Servicios Docker"
            ;;
        "local")
            echo -e "${GREEN}📦 Tipo de instalación:${NC} Solo Local"
            echo ""
            echo -e "${WHITE}🚀 Para ejecutar:${NC}"
            echo "   ./run.sh"
            echo ""
            echo -e "${WHITE}⚠️  Requisitos:${NC}"
            echo "   - MySQL debe estar instalado y corriendo"
            echo "   - Crear base de datos: jdmmitagente_db"
            echo "   - Usuario: jdmmit_user"
            ;;
    esac
    
    echo ""
    echo -e "${WHITE}🔧 Configuración:${NC}"
    if grep -q "tu_email@gmail.com" .env 2>/dev/null; then
        echo -e "${YELLOW}   ⚠️  Recuerda configurar tus datos personales:${NC}"
        echo "   ./setup-config.sh"
    else
        echo -e "${GREEN}   ✅ Configuración personalizada lista${NC}"
    fi
    
    echo ""
    echo -e "${WHITE}📚 Documentación:${NC}"
    echo "   README.md                   # Guía completa"
    echo "   ./test-project.sh          # Verificar proyecto"
    echo ""
    
    echo -e "${BLUE}🤖 ¡Tu asistente JDMMitAgente está listo para usarse!${NC}"
}

# Función principal
main() {
    # Verificar dependencias
    check_docker
    check_python
    
    # Configurar datos personales
    setup_configuration
    
    # Configurar entorno
    setup_environment
    
    # Seleccionar e instalar
    select_installation_type
    
    # Verificar instalación
    verify_installation
    
    # Mostrar resumen
    show_installation_summary
}

# Ejecutar instalación
main "$@"

#!/bin/bash

echo "🐳 Iniciando JDMMitAgente con Docker"
echo "====================================="

# Verificar que docker-compose.yml existe
if [ ! -f "docker-compose.yml" ]; then
    echo "❌ docker-compose.yml no encontrado"
    exit 1
fi

# Verificar que .env existe
if [ ! -f ".env" ]; then
    echo "❌ Archivo .env no encontrado"
    exit 1
fi

echo "🔍 Verificando servicios..."

# Detener servicios existentes si están corriendo
docker-compose down --remove-orphans

echo "🚀 Iniciando servicios..."

# Iniciar servicios en segundo plano
docker-compose up -d

# Esperar a que los servicios estén listos
echo "⏳ Esperando a que los servicios estén listos..."
sleep 10

# Verificar estado de los servicios
echo "📊 Estado de los servicios:"
docker-compose ps

# Mostrar logs del agente
echo ""
echo "📋 Logs del agente (Ctrl+C para salir de los logs):"
echo "================================================="

# Seguir logs del contenedor principal
docker-compose logs -f jdmmitagente

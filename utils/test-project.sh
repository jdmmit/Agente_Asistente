#!/bin/bash

echo "🧪 Verificación Rápida del Proyecto JDMMitAgente"
echo "==============================================="

# Verificar estructura de archivos
echo "📁 Verificando estructura de archivos..."
required_files=(
    "jdmmitagente.py"
    "config.py"
    "requirements.txt"
    "docker-compose.yml"
    "Dockerfile"
    ".env"
    "install.sh"
    "run.sh"
    "run-docker.sh"
    "README.md"
    "db_init/init.sql"
)

missing_files=0
for file in "${required_files[@]}"; do
    if [ -f "$file" ]; then
        echo "  ✅ $file"
    else
        echo "  ❌ $file - FALTANTE"
        ((missing_files++))
    fi
done

if [ $missing_files -eq 0 ]; then
    echo "✅ Todos los archivos requeridos están presentes"
else
    echo "❌ Faltan $missing_files archivos"
    exit 1
fi

# Verificar permisos de scripts
echo ""
echo "🔒 Verificando permisos de scripts..."
scripts=("install.sh" "run.sh" "run-docker.sh" "jdmmitagente.py")
for script in "${scripts[@]}"; do
    if [ -x "$script" ]; then
        echo "  ✅ $script - ejecutable"
    else
        echo "  ⚠️  $script - sin permisos de ejecución"
        chmod +x "$script"
        echo "  🔧 Permisos corregidos para $script"
    fi
done

# Verificar sintaxis Python
echo ""
echo "🐍 Verificando sintaxis Python..."
if python3 -m py_compile jdmmitagente.py; then
    echo "  ✅ jdmmitagente.py - sintaxis correcta"
else
    echo "  ❌ jdmmitagente.py - errores de sintaxis"
    exit 1
fi

if python3 -m py_compile config.py; then
    echo "  ✅ config.py - sintaxis correcta"
else
    echo "  ❌ config.py - errores de sintaxis"
    exit 1
fi

# Verificar Docker compose
echo ""
echo "🐳 Verificando Docker Compose..."
if command -v docker-compose &> /dev/null; then
    if docker-compose config > /dev/null 2>&1; then
        echo "  ✅ docker-compose.yml - configuración válida"
    else
        echo "  ❌ docker-compose.yml - configuración inválida"
        exit 1
    fi
else
    echo "  ⚠️  Docker Compose no instalado - omitiendo verificación"
fi

# Verificar variables de entorno
echo ""
echo "🔧 Verificando archivo .env..."
required_vars=("MODEL" "DB_TYPE" "DB_HOST" "DB_USER" "DB_PASSWORD" "DB_NAME")
missing_vars=0
for var in "${required_vars[@]}"; do
    if grep -q "^$var=" .env; then
        echo "  ✅ $var - configurado"
    else
        echo "  ❌ $var - FALTANTE en .env"
        ((missing_vars++))
    fi
done

if [ $missing_vars -eq 0 ]; then
    echo "✅ Todas las variables de entorno están configuradas"
else
    echo "❌ Faltan $missing_vars variables en .env"
fi

# Resumen final
echo ""
echo "📋 RESUMEN DE VERIFICACIÓN"
echo "=========================="
if [ $missing_files -eq 0 ] && [ $missing_vars -eq 0 ]; then
    echo "🎉 ¡Proyecto verificado exitosamente!"
    echo ""
    echo "🚀 Para ejecutar el proyecto:"
    echo "  1. Ejecutar instalador: ./install.sh"
    echo "  2. Iniciar con Docker:   ./run-docker.sh"
    echo "  3. O ejecutar local:     ./run.sh"
else
    echo "⚠️  Se encontraron algunos problemas. Revisa los mensajes anteriores."
fi

echo ""
echo "📚 Documentación disponible en README.md"

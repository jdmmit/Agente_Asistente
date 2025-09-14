#!/bin/bash

echo "🏠 Ejecutando JDMMitAgente localmente"
echo "===================================="

# Verificar si el entorno virtual existe
if [ ! -d "venv" ]; then
    echo "❌ Entorno virtual no encontrado. Ejecuta ./install.sh primero."
    exit 1
fi

# Verificar que .env existe
if [ ! -f ".env" ]; then
    echo "❌ Archivo .env no encontrado"
    exit 1
fi

# Activar entorno virtual
source venv/bin/activate

# Verificar que las dependencias están instaladas
echo "🔍 Verificando dependencias..."
pip show mysql-connector-python > /dev/null
if [ $? -ne 0 ]; then
    echo "❌ Dependencias no encontradas. Instalando..."
    pip install -r requirements.txt
fi

# Verificar conexión a MySQL (si es local)
DB_HOST=$(grep DB_HOST .env | cut -d'=' -f2 | tr -d "'" | tr -d '"')
if [ "$DB_HOST" = "localhost" ] || [ "$DB_HOST" = "127.0.0.1" ]; then
    echo "🔍 Verificando MySQL local..."
    if ! command -v mysql &> /dev/null; then
        echo "⚠️  Cliente MySQL no encontrado. Intentando continuar..."
    else
        DB_USER=$(grep DB_USER .env | cut -d'=' -f2 | tr -d "'" | tr -d '"')
        DB_PASS=$(grep DB_PASSWORD .env | cut -d'=' -f2 | tr -d "'" | tr -d '"')
        DB_NAME=$(grep DB_NAME .env | cut -d'=' -f2 | tr -d "'" | tr -d '"')
        
        mysql -u"$DB_USER" -p"$DB_PASS" -e "USE $DB_NAME;" 2>/dev/null
        if [ $? -ne 0 ]; then
            echo "❌ No se puede conectar a MySQL local. Verifica la configuración."
            exit 1
        fi
        echo "✅ Conexión a MySQL verificada"
    fi
fi

echo "🚀 Iniciando JDMMitAgente..."
echo ""

# Ejecutar el agente
python jdmmitagente.py "$@"

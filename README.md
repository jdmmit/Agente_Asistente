# 🤖 JDMMitAgente v3.0.0

**Asistente Inteligente Optimizado con MySQL y funcionalidades avanzadas**

JDMMitAgente es un asistente inteligente con capacidades de conversación, gestión de tareas, memoria persistente y múltiples formas de comunicación (voz, WhatsApp, email, notificaciones).

## 🚀 Características

### ✨ Funcionalidades Principales
- 💬 **Conversación Inteligente**: Interfaz natural usando Ollama
- 🧠 **Memoria Persistente**: Base de datos MySQL para historial y memoria a largo plazo
- 🎤 **Reconocimiento de Voz**: Entrada por voz usando Google Speech Recognition
- 🔊 **Síntesis de Voz**: Respuestas habladas con pyttsx3 y gTTS como fallback
- 📋 **Gestión de Tareas**: Crear, listar y completar tareas programadas
- 💾 **Memoria Inteligente**: Categorización automática de información importante

### 📱 Comunicaciones
- 📧 **Email**: Envío de emails automatizado
- 📱 **WhatsApp**: Integración con WhatsApp Web
- 🔔 **Notificaciones**: Notificaciones locales del sistema

### 🏗️ Arquitectura
- 🐳 **Docker**: Despliegue containerizado completo
- 🗄️ **MySQL**: Base de datos robusta y escalable
- 🦙 **Ollama**: Modelos de lenguaje local
- 🐍 **Python 3.11**: Backend optimizado

## 🎯 Configuración Personalizada

**¡NUEVO!** JDMMitAgente ahora incluye un configurador interactivo que te permite usar tus propios datos personales de forma segura.

### 🚀 Configuración Rápida en 3 Pasos

```bash
# 1. Descargar el proyecto
git clone <repository-url>
cd Agente_Asistente

# 2. Configurar tus datos personales
./setup-config.sh

# 3. Instalar y ejecutar
./install.sh
./run-docker.sh
```

### 🎨 Tipos de Configuración Disponibles

- **🏠 Personal:** Para uso doméstico con tu Gmail y WhatsApp
- **🏢 Empresarial:** Para uso corporativo con email empresarial
- **🧪 Desarrollo:** Configuración rápida para testing
- **⚙️ Avanzada:** Control total sobre todas las opciones

**📚 [Ver Guía Completa de Configuración](README-CONFIGURACION.md)**

### 🔐 Seguridad y Privacidad
- ✅ Validación automática de emails y teléfonos
- ✅ Contraseñas encriptadas opcionalmente
- ✅ Backups automáticos de configuración
- ✅ Permisos restrictivos en archivos sensibles


## 📦 Instalación Rápida

### Prerrequisitos
- Docker y Docker Compose
- Python 3.8+ (opcional, para ejecución local)

### 1. Clonar e Instalar
```bash
git clone <repository-url>
cd Agente_Asistente
./install.sh
```

### 2. Configurar (Opcional)
Edita el archivo `.env` para personalizar configuraciones:
```bash
nano .env
```

### 3. Ejecutar
```bash
# Con Docker (recomendado)
./run-docker.sh

# Localmente (requiere MySQL local)
./run.sh
```

## 🔧 Configuración

### Variables de Entorno (.env)
```bash
# Modelo de IA
MODEL='llama3.2'

# Base de Datos MySQL
DB_TYPE='mysql'
DB_HOST='mysql'  # 'localhost' para instalación local
DB_PORT='3306'
DB_USER='jdmmit_user'
DB_PASSWORD='jdmmit_password'
DB_NAME='jdmmitagente_db'

# Configuración de Email
EMAIL_SMTP='smtp.gmail.com'
EMAIL_PORT='587'
EMAIL_USER='tu_email@gmail.com'
EMAIL_PASS='tu_app_password'

# WhatsApp
WHATSAPP_NUMBER='+1234567890'

# Otros
GOOGLE_SPEECH_LANGUAGE='es-ES'
LOG_FILE='jdmmitagente.log'
```

## 🎯 Uso

### Comandos de Conversación
```bash
# Modo interactivo completo
./run-docker.sh

# Comando único
python jdmmitagente.py -c "¿Qué tareas tengo pendientes?"

# Con argumentos específicos
python jdmmitagente.py --command "Recuérdame llamar al doctor mañana a las 10am"
```

### Ejemplos de Interacción

#### Gestión de Tareas
```
👤 Recuérdame enviar el reporte el viernes a las 2pm
🤖 ✅ Tarea guardada: enviar el reporte para 2024-XX-XX 14:00

👤 ¿Qué tareas tengo?
🤖 📋 Tus tareas pendientes:
• ID 1: enviar el reporte
  📅 2024-XX-XX 14:00
  📝 Preparar reporte mensual
```

#### Memoria Inteligente
```
👤 Guarda que mi reunión semanal es los lunes a las 10am
🤖 🧠 Información guardada en memoria (categoría: general)

👤 ¿Cuándo es mi reunión?
🤖 Tu reunión semanal es los lunes a las 10am
```

### Modo Voz
```
👤 voz
🤖 🎤 Modo voz activado
🎤 Escuchando...
👤 (hablando) Crea una tarea para comprar leche
🤖 ✅ Tarea guardada: comprar leche...
```

## 🐳 Docker

### Servicios
- **jdmmitagente**: Aplicación principal
- **mysql**: Base de datos MySQL 8.0
- **ollama**: Servidor de modelos de IA

### Comandos Docker
```bash
# Iniciar servicios
docker-compose up -d

# Ver logs
docker-compose logs -f jdmmitagente

# Detener servicios
docker-compose down

# Reconstruir
docker-compose build --no-cache

# Estado de servicios
docker-compose ps
```

## 🗄️ Base de Datos

### Estructura de Tablas
- **conversations**: Historial de conversaciones
- **scheduled_tasks**: Tareas programadas
- **long_term_memory**: Memoria a largo plazo
- **user_configs**: Configuraciones personalizadas

### Acceso a MySQL
```bash
# Dentro del contenedor
docker-compose exec mysql mysql -u jdmmit_user -p jdmmitagente_db

# Desde host (si el puerto está expuesto)
mysql -h localhost -P 3306 -u jdmmit_user -p jdmmitagente_db
```

## 📁 Estructura del Proyecto

```
Agente_Asistente/
├── jdmmitagente.py      # Aplicación principal optimizada
├── config.py            # Configuraciones centralizadas
├── requirements.txt     # Dependencias Python
├── docker-compose.yml   # Orquestación de servicios
├── Dockerfile           # Imagen de la aplicación
├── .env                 # Variables de entorno
├── db_init/            # Scripts de inicialización de DB
│   └── init.sql
├── install.sh          # Instalador automático
├── run-docker.sh       # Ejecutor Docker
├── run.sh              # Ejecutor local
└── README.md           # Esta documentación
```

## 🚀 Desarrollo

### Instalación para Desarrollo
```bash
# Clonar repositorio
git clone <repository-url>
cd Agente_Asistente

# Crear entorno virtual
python3 -m venv venv
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt

# Instalar herramientas de desarrollo
pip install black flake8 pytest

# Formatear código
black .

# Linting
flake8 --max-line-length=100 jdmmitagente.py

# Ejecutar tests
pytest
```

### Agregar Nuevas Funcionalidades
1. Modificar `jdmmitagente.py`
2. Actualizar `config.py` si es necesario
3. Agregar dependencias a `requirements.txt`
4. Actualizar documentación
5. Crear pruebas en `tests/`

## 🔒 Seguridad

- ✅ Usuario no-root en Docker
- ✅ Variables de entorno para secretos
- ✅ Validación de entrada
- ✅ Logs estructurados
- ✅ Conexiones SSL para email

## 🛠️ Solución de Problemas

### Problemas Comunes

#### Error de conexión a MySQL
```bash
# Verificar que MySQL esté corriendo
docker-compose ps

# Reiniciar servicios
docker-compose restart mysql
```

#### Problemas de voz
```bash
# En sistemas sin audio
export PULSE_SERVER=unix:${XDG_RUNTIME_DIR}/pulse/native
```

#### Permisos de archivos
```bash
chmod +x *.sh
chmod +x jdmmitagente.py
```

### Logs y Depuración
```bash
# Ver logs de la aplicación
tail -f jdmmitagente.log

# Logs de Docker
docker-compose logs -f

# Logs de MySQL
docker-compose logs mysql

# Entrar al contenedor para debug
docker-compose exec jdmmitagente bash
```

## 📊 Monitoreo

### Métricas Disponibles
- Conversaciones por día
- Tareas creadas/completadas
- Uptime de servicios
- Uso de memoria y CPU

### Comandos de Monitoreo
```bash
# Estado de servicios
docker-compose ps

# Uso de recursos
docker stats $(docker-compose ps -q)

# Espacio en disco
docker system df
```

## 🤝 Contribuir

1. Fork el proyecto
2. Crea una rama para tu funcionalidad (`git checkout -b feature/nueva-funcionalidad`)
3. Commit tus cambios (`git commit -am 'Agregar nueva funcionalidad'`)
4. Push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Crear un Pull Request

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo `LICENSE` para más detalles.

## 🆘 Soporte

- 📧 Email: soporte@jdmmitagente.com
- 📱 WhatsApp: +573015371477
- 🐛 Issues: [GitHub Issues](repository-issues-url)

## 📈 Roadmap

### v3.1.0 (Próximamente)
- [ ] Interfaz web con Streamlit
- [ ] API REST para integraciones
- [ ] Soporte para más modelos de IA
- [ ] Análisis de sentimientos

### v3.2.0
- [ ] Integración con calendarios
- [ ] Recordatorios inteligentes
- [ ] Exportación de datos
- [ ] Modo multi-usuario

---

**🤖 JDMMitAgente v3.0.0** - Tu asistente inteligente personal

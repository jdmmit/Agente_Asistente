# 🔧 Guía de Configuración Personalizada - JDMMitAgente

Esta guía te ayudará a configurar JDMMitAgente con tus datos personales de forma segura y fácil.

## 🚀 Configuración Rápida

### Método 1: Configuración Automática (Recomendado)

```bash
# 1. Ejecutar instalador que incluye configuración
./install.sh

# 2. Seguir el asistente interactivo
# El instalador detectará si necesitas configurar y te guiará
```

### Método 2: Configuración Manual

```bash
# 1. Ejecutar configurador independiente
./setup-config.sh

# 2. Luego instalar
./install.sh
```

## 🎯 Tipos de Configuración

### 🏠 Personal (Recomendado para la mayoría)
**Ideal para:** Uso doméstico, asistente personal

**Incluye:**
- Configuración de email personal (Gmail recomendado)
- WhatsApp opcional
- Configuraciones de voz habilitadas
- Notificaciones activas
- Privacidad alta

**Datos requeridos:**
- Tu nombre completo
- Email personal
- Contraseña de aplicación (Gmail)
- Número WhatsApp (opcional)

### 🏢 Empresarial
**Ideal para:** Uso en oficina, empresa, equipos

**Incluye:**
- Email corporativo
- Base de datos remota opcional
- Configuraciones de auditoría
- Modo multi-usuario
- Voz deshabilitada por defecto

**Datos requeridos:**
- Nombre de la empresa
- Email corporativo
- Servidor SMTP empresarial
- Configuración de BD (local o remota)

### 🧪 Desarrollo
**Ideal para:** Desarrolladores, testing, pruebas

**Incluye:**
- Datos de prueba predefinidos
- Modo debug activado
- Logs detallados
- Configuración rápida sin datos reales

**Sin datos requeridos:** Se configuran automáticamente

### ⚙️ Avanzada
**Ideal para:** Usuarios expertos, configuraciones específicas

**Incluye:**
- Control total sobre todas las opciones
- Selección de modelo de IA
- Configuraciones específicas
- Opciones de servidor personalizado

## 📋 Proceso de Configuración Detallado

### Paso 1: Preparación
Antes de comenzar, ten a mano:

**Para uso Personal:**
- Tu email de Gmail
- Una "App Password" de Google ([Generar aquí](https://myaccount.google.com/apppasswords))
- Tu número WhatsApp (formato: +573015371477)

**Para uso Empresarial:**
- Email corporativo
- Configuraciones SMTP de tu empresa
- Datos de base de datos (si usas remota)

### Paso 2: Ejecutar Configurador

```bash
./setup-config.sh
```

### Paso 3: Seleccionar Tipo
El configurador te presentará un menú:
```
🎯 Configuración de JDMMitAgente
Esta herramienta te ayudará a configurar tu asistente personal.

📋 Tipo de configuración:
1. 🏠 Uso Personal (recomendado)
2. 🏢 Uso Empresarial  
3. 🧪 Desarrollo/Testing
4. ⚙️  Configuración Avanzada

Elige una opción [1-4]: 1
```

### Paso 4: Completar Datos
Según el tipo elegido, el configurador te pedirá:

**Configuración Personal:**
```
📝 Información Personal:
Tu nombre completo: Juan Pérez
Nombre de tu asistente [JDMMitAgente]: MiAsistente

📧 Configuración de Email:
Tu email (Gmail recomendado): juan.perez@gmail.com
💡 Para Gmail, usa una 'App Password' en lugar de tu contraseña normal.
   Genera una en: https://myaccount.google.com/apppasswords
Contraseña/App Password: ********

📱 WhatsApp (opcional):
¿Configurar WhatsApp? (s/n): s
Número WhatsApp (formato +1234567890): +573015371477
```

### Paso 5: Confirmación
El configurador mostrará un resumen:
```
📋 Resumen de Configuración:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
👤 Propietario: Juan Pérez
🤖 Asistente: MiAsistente
📧 Email: juan.perez@gmail.com
📱 WhatsApp: +573015371477
🗄️  Base de Datos: MySQL (mysql)
🤖 Modelo IA: llama3.2
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

¿La configuración es correcta? (s/n): s
```

## 🔐 Seguridad y Privacidad

### Protección de Datos
- Todas las contraseñas se almacenan de forma segura
- El archivo `.env` tiene permisos restrictivos (600)
- Se crean backups automáticamente

### Encriptación de Datos Sensibles
Para mayor seguridad, puedes encriptar tu configuración:

```bash
# Encriptar archivo .env
./secure-env.sh encrypt

# Desencriptar cuando lo necesites
./secure-env.sh decrypt

# Crear backup encriptado
./secure-env.sh backup

# Verificar integridad
./secure-env.sh check
```

### Reconfiguración Segura
Si necesitas cambiar datos:

```bash
# Reconfigurar completamente
./setup-config.sh

# O editar manualmente (cuidado con la sintaxis)
nano .env
```

## 🛠️ Configuraciones Especiales

### Gmail: Configurar App Password

1. Ve a [myaccount.google.com](https://myaccount.google.com)
2. Seguridad → Verificación en dos pasos
3. App passwords → Seleccionar aplicación → Otro
4. Nombre: "JDMMitAgente"
5. Copiar la contraseña generada (16 caracteres)

### WhatsApp: Formato de Número

```
✅ Correcto: +573015371477
✅ Correcto: +14155551234
❌ Incorrecto: 3015371477
❌ Incorrecto: (301) 537-1477
```

### Configuración Empresarial: SMTP

Servidores SMTP comunes:
```bash
# Gmail Empresarial
EMAIL_SMTP='smtp.gmail.com'
EMAIL_PORT='587'

# Outlook/Exchange
EMAIL_SMTP='smtp-mail.outlook.com'  
EMAIL_PORT='587'

# Yahoo
EMAIL_SMTP='smtp.mail.yahoo.com'
EMAIL_PORT='587'
```

## 🔄 Reconfiguración

### Cambiar Datos Personales
```bash
# Método 1: Configurador completo
./setup-config.sh

# Método 2: Solo datos sensibles
./setup-config.sh --personal-data

# Método 3: Resetear y empezar de nuevo
./setup-config.sh --reset
```

### Migrar Configuración
```bash
# Hacer backup de configuración actual
./secure-env.sh backup

# Reconfigurar
./setup-config.sh

# Si algo sale mal, restaurar
./secure-env.sh restore
```

## 🐛 Solución de Problemas

### Error: Email inválido
```bash
❌ Email inválido. Intenta de nuevo.
```
**Solución:** Verifica el formato: usuario@dominio.com

### Error: Número de teléfono inválido
```bash
❌ Número inválido. Formato: +1234567890
```
**Solución:** Usa formato internacional: +[código país][número]

### Error: Configuración no funciona
```bash
# Verificar integridad
./secure-env.sh check

# Ver archivo de configuración
cat .env | grep -v PASSWORD  # Oculta contraseñas
```

### Regenerar Configuración por Defecto
```bash
# Respaldar actual
mv .env .env.backup

# Generar nueva con defaults
./setup-config.sh --defaults
```

## 📚 Plantillas Disponibles

El proyecto incluye plantillas para diferentes usos:

```bash
templates/
├── personal.env.template     # Uso personal
├── business.env.template     # Uso empresarial  
└── development.env.template  # Desarrollo
```

Puedes basarte en estas plantillas para configuraciones personalizadas.

## ✨ Configuraciones Avanzadas

### Variables Adicionales

Puedes agregar estas variables a tu `.env` para funcionalidades extra:

```bash
# Configuraciones de comportamiento
NOTIFICATION_ENABLED='true'
VOICE_ENABLED='true'
AUTO_BACKUP='true'
PRIVACY_MODE='high'

# Logging
LOG_LEVEL='INFO'  # DEBUG, INFO, WARNING, ERROR
DEBUG_MODE='false'

# Rendimiento  
MAX_CONVERSATIONS='1000'
CLEANUP_DAYS='30'
```

### Modo Multi-Usuario (Empresarial)
```bash
MULTI_USER='true'
ADMIN_EMAIL='admin@empresa.com'
USER_ROLES='admin,user,guest'
```

---

## 🎉 ¡Configuración Completada!

Una vez configurado:

1. **Ejecutar instalador:** `./install.sh`
2. **Iniciar asistente:** `./run-docker.sh`
3. **Probar funcionalidades:** Email, WhatsApp, voz
4. **Crear backup:** `./secure-env.sh backup`

¿Necesitas ayuda? Consulta el README principal o ejecuta:
```bash
./setup-config.sh --help
./secure-env.sh --help
```

**🤖 ¡Tu JDMMitAgente personalizado está listo!**

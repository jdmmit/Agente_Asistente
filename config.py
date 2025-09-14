from dotenv import load_dotenv
import os

# Cargar .env si existe
load_dotenv()

# Configuraciones principales
MODEL = os.getenv('MODEL', 'llama3.2')

# Configuraciones de base de datos MySQL
DB_TYPE = os.getenv('DB_TYPE', 'mysql')
DB_HOST = os.getenv('DB_HOST', 'mysql')
DB_PORT = int(os.getenv('DB_PORT', '3306'))
DB_USER = os.getenv('DB_USER', 'jdmmit_user')
DB_PASSWORD = os.getenv('DB_PASSWORD', 'jdmmit_password')
DB_NAME = os.getenv('DB_NAME', 'jdmmitagente_db')

# Configuración de conexión completa para MySQL
DB_CONFIG = {
    'host': DB_HOST,
    'port': DB_PORT,
    'user': DB_USER,
    'password': DB_PASSWORD,
    'database': DB_NAME,
    'charset': 'utf8mb4',
    'autocommit': True,
    'auth_plugin': 'mysql_native_password'
}

# Configuraciones de email
EMAIL_SMTP = os.getenv('EMAIL_SMTP', 'smtp.gmail.com')
EMAIL_PORT = int(os.getenv('EMAIL_PORT', '587'))
EMAIL_USER = os.getenv('EMAIL_USER', 'jdmmitagente@gmail.com')
EMAIL_PASS = os.getenv('EMAIL_PASS', 'tu_app_password')

# Número de WhatsApp
WHATSAPP_NUMBER = os.getenv('WHATSAPP_NUMBER', '+573015371477')

# Configuraciones de voz
GOOGLE_SPEECH_LANGUAGE = os.getenv('GOOGLE_SPEECH_LANGUAGE', 'es-ES')

# Configuraciones específicas de JDMMitAgente
ASSISTANT_NAME = 'JDMMitAgente'
ASSISTANT_VERSION = '3.0.0'
LOG_FILE = os.getenv('LOG_FILE', 'jdmmitagente.log')

# Configuraciones de Ollama
OLLAMA_HOST = os.getenv('OLLAMA_HOST', 'http://localhost:11434')


import os
import logging
import sqlite3
import mysql.connector
from config import DB_CONFIG

logger = logging.getLogger(__name__)

class DatabaseManager:
    """
    Gestor de base de datos bimodal (MySQL/SQLite).
    Detecta automáticamente qué motor de base de datos usar basándose en la variable de entorno DATABASE_NAME.
    - Si DATABASE_NAME termina en .db, usa SQLite.
    - De lo contrario, usa la configuración de MySQL de DB_CONFIG.
    """

    def __init__(self):
        self.db_name = os.getenv('DATABASE_NAME')
        self.connection = None
        self.db_type = 'sqlite' if self.db_name and self.db_name.endswith('.db') else 'mysql'
        
        self.connect()
        if self.db_type == 'sqlite':
            self.init_db_schema()

    def connect(self):
        """Establece la conexión con la base de datos adecuada."""
        try:
            if self.db_type == 'sqlite':
                self.connection = sqlite3.connect(self.db_name, check_same_thread=False)
                # Row factory para obtener resultados como diccionarios, similar a dictionary=True en MySQL
                self.connection.row_factory = sqlite3.Row
                logger.info(f"Conexión a SQLite establecida exitosamente: {self.db_name}")
            else:
                self.connection = mysql.connector.connect(**DB_CONFIG)
                logger.info("Conexión a MySQL establecida exitosamente")
        except (sqlite3.Error, mysql.connector.Error) as e:
            logger.error(f"Error conectando a la base de datos ({self.db_type}): {e}")
            raise

    def init_db_schema(self):
        """
        (Solo SQLite) Crea el esquema de la base de datos si las tablas no existen.
        Esto asegura que el entorno de pruebas siempre esté listo.
        """
        # MySQL/Docker maneja esto a través del script init.sql
        if self.db_type != 'sqlite':
            return

        schema = [
            """
            CREATE TABLE IF NOT EXISTS conversations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                user_message TEXT NOT NULL,
                assistant_message TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            );
            """,
            """
            CREATE TABLE IF NOT EXISTS memories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                category TEXT NOT NULL,
                key TEXT NOT NULL UNIQUE,
                value TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            );
            """,
            """
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task_name TEXT NOT NULL,
                description TEXT,
                scheduled_time DATETIME,
                status TEXT NOT NULL DEFAULT 'pending',
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                completed_at DATETIME
            );
            """
        ]
        
        try:
            cursor = self.connection.cursor()
            for table_query in schema:
                cursor.execute(table_query)
            self.connection.commit()
            logger.info("Esquema de base de datos SQLite verificado/creado.")
        except sqlite3.Error as e:
            logger.error(f"Error inicializando el esquema de SQLite: {e}")
            raise

    def _get_placeholder(self, count=1):
        """Devuelve el marcador de posición correcto para la consulta según el tipo de BD."""
        if self.db_type == 'sqlite':
            return '?' if count == 1 else ', '.join(['?'] * count)
        return '%s' if count == 1 else ', '.join(['%s'] * count)

    def execute_query(self, query, params=None, fetch=None):
        """
        Ejecuta una consulta con la sintaxis y el manejo de errores adecuados para el motor de BD actual.
        Fetch puede ser 'one' o 'all'.
        """
        # Reemplazar %s por ? para SQLite
        if self.db_type == 'sqlite':
            query = query.replace('%s', '?')
            # SQLite no soporta ON DUPLICATE KEY UPDATE, se maneja en el método que lo llama
            # NOW() se reemplaza por CURRENT_TIMESTAMP
            query = query.replace('NOW()', 'CURRENT_TIMESTAMP')

        try:
            # MySQL necesita cursores con dictionary=True que se abren y cierran
            if self.db_type == 'mysql':
                cursor = self.connection.cursor(dictionary=True)
            else:
            # SQLite usa un cursor estándar y la row_factory se encarga de los diccionarios
                cursor = self.connection.cursor()
            
            cursor.execute(query, params or ())

            if fetch == 'one':
                result = cursor.fetchone()
                return dict(result) if result else None
            elif fetch == 'all':
                results = cursor.fetchall()
                return [dict(row) for row in results]
            else:
                self.connection.commit()
                return True

        except (sqlite3.Error, mysql.connector.Error) as e:
            logger.error(f"Error de base de datos ({self.db_type}) en la consulta: {query} | Error: {e}")
            if self.db_type == 'mysql' and e.errno in (2006, 2013):
                logger.info("Reconectando a la base de datos MySQL...")
                self.connect()
                return self.execute_query(query, params, fetch) # Reintentar
            if self.db_type == 'sqlite':
                self.connection.rollback()
            return False
        finally:
            if self.db_type == 'mysql' and 'cursor' in locals():
                cursor.close()

    def save_conversation(self, user_message, assistant_message, session_id):
        query = "INSERT INTO conversations (user_message, assistant_message, session_id) VALUES ({placeholders})"
        query = query.format(placeholders=self._get_placeholder(3))
        return self.execute_query(query, (user_message, assistant_message, session_id))

    def get_recent_conversations(self, limit=5):
        query = f"SELECT user_message, assistant_message FROM conversations ORDER BY timestamp DESC LIMIT {self._get_placeholder()}"
        return list(reversed(self.execute_query(query, (limit,), fetch='all')))

    def save_task(self, task_name, description, scheduled_time):
        query = "INSERT INTO tasks (task_name, description, scheduled_time) VALUES ({placeholders})"
        query = query.format(placeholders=self._get_placeholder(3))
        return self.execute_query(query, (task_name, description, scheduled_time))

    def get_pending_tasks(self):
        query = "SELECT id, task_name, description, scheduled_time FROM tasks WHERE status = 'pending' ORDER BY scheduled_time"
        return self.execute_query(query, fetch='all')

    def complete_task(self, task_id):
        query = f"UPDATE tasks SET status = 'completed', completed_at = NOW() WHERE id = {self._get_placeholder()}"
        return self.execute_query(query, (task_id,))

    def save_memory(self, category, key, value):
        if self.db_type == 'sqlite':
            query = f"""
            INSERT INTO memories (category, key, value) VALUES (?, ?, ?)
            ON CONFLICT(key) DO UPDATE SET
                value = excluded.value,
                updated_at = CURRENT_TIMESTAMP;
            """
            params = (category, key, value)
        else: # MySQL
            query = f"""
            INSERT INTO memories (category, key, value) VALUES (%s, %s, %s)
            ON DUPLICATE KEY UPDATE
                value = VALUES(value),
                updated_at = NOW();
            """
            params = (category, key, value)
        
        return self.execute_query(query, params)

    def get_memory(self, key):
        query = f"SELECT id, category, key, value FROM memories WHERE key = {self._get_placeholder()}"
        return self.execute_query(query, (key,), fetch='one')

    def close(self):
        """Cierra la conexión a la base de datos si está abierta."""
        if self.connection:
            try:
                self.connection.close()
                logger.info(f"Conexión a {self.db_type} cerrada.")
            except (sqlite3.Error, mysql.connector.Error) as e:
                logger.error(f"Error al cerrar la conexión de {self.db_type}: {e}")


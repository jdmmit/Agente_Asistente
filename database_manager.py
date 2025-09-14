
import logging
import mysql.connector
import uuid
from datetime import datetime

from config import DB_CONFIG

logger = logging.getLogger(__name__)


class DatabaseManager:
    """Gestor de base de datos MySQL optimizado"""

    def __init__(self):
        self.db_config = DB_CONFIG
        self.connection = None
        self.connect()

    def connect(self):
        """Conectar a la base de datos MySQL"""
        try:
            self.connection = mysql.connector.connect(**self.db_config)
            logger.info("Conexión a MySQL establecida exitosamente")
        except mysql.connector.Error as e:
            logger.error(f"Error conectando a MySQL: {e}")
            raise

    def execute_query(self, query, params=None, fetch=False):
        """Ejecutar query con manejo de errores"""
        try:
            # Usar un nuevo cursor para cada operación en un entorno multi-hilo
            with self.connection.cursor(dictionary=True) as cursor:
                cursor.execute(query, params or ())
                
                if fetch:
                    result = cursor.fetchall()
                    return result
                else:
                    self.connection.commit()
                    return True
                    
        except mysql.connector.Error as e:
            logger.error(f"Error ejecutando query: {e}")
            # Re-conectar si la conexión se ha perdido
            if e.errno in (2006, 2013):
                logger.info("Reconectando a la base de datos...")
                self.connect()
                # Re-intentar la query una vez
                return self.execute_query(query, params, fetch)
            self.connection.rollback()
            return False
    
    def save_conversation(self, user_message, assistant_message, session_id=None):
        """Guardar conversación en la base de datos"""
        query = """
        INSERT INTO conversations (user_message, assistant_message, session_id)
        VALUES (%s, %s, %s)
        """
        session_id = session_id or str(uuid.uuid4())
        return self.execute_query(query, (user_message, assistant_message, session_id))
    
    def get_recent_conversations(self, limit=5):
        """Obtener conversaciones recientes"""
        query = """
        SELECT user_message, assistant_message, timestamp 
        FROM conversations 
        ORDER BY timestamp DESC 
        LIMIT %s
        """
        result = self.execute_query(query, (limit,), fetch=True)
        return list(reversed(result)) if result else []
    
    def save_task(self, task_name, description, scheduled_time=None, status='pending'):
        """Guardar tarea programada"""
        query = """
        INSERT INTO scheduled_tasks (task_name, description, scheduled_time, status)
        VALUES (%s, %s, %s, %s)
        """
        scheduled_time = scheduled_time or datetime.now()
        return self.execute_query(query, (task_name, description, scheduled_time, status))
    
    def get_pending_tasks(self):
        """Obtener tareas pendientes"""
        query = """
        SELECT id, task_name, description, scheduled_time, status
        FROM scheduled_tasks 
        WHERE status = 'pending'
        ORDER BY scheduled_time
        """
        return self.execute_query(query, fetch=True)
    
    def complete_task(self, task_id):
        """Marcar tarea como completada"""
        query = """
        UPDATE scheduled_tasks 
        SET status = 'completed', completed_at = NOW()
        WHERE id = %s
        """
        return self.execute_query(query, (task_id,))
    
    def save_memory(self, category, key_info, details, importance_level=1):
        """Guardar información en memoria a largo plazo"""
        query = """
        INSERT INTO long_term_memory (category, key_info, details, importance_level)
        VALUES (%s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE 
        details = VALUES(details),
        importance_level = VALUES(importance_level),
        updated_at = NOW()
        """
        return self.execute_query(query, (category, key_info, details, importance_level))
    
    def get_memory(self, category=None, limit=10):
        """Obtener información de memoria"""
        if category:
            query = """
            SELECT * FROM long_term_memory 
            WHERE category = %s 
            ORDER BY importance_level DESC, updated_at DESC
            LIMIT %s
            """
            params = (category, limit)
        else:
            query = """
            SELECT * FROM long_term_memory 
            ORDER BY importance_level DESC, updated_at DESC
            LIMIT %s
            """
            params = (limit,)
        
        return self.execute_query(query, params, fetch=True)

    def close(self):
        """Cerrar la conexión a la base de datos"""
        if self.connection and self.connection.is_connected():
            self.connection.close()
            logger.info("Conexión a MySQL cerrada")


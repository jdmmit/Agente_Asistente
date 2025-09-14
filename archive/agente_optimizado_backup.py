"""
Agente Memorae Optimizado
Versión mejorada del asistente AI con mejor arquitectura y manejo de errores
"""

import os
import logging
from dataclasses import dataclass
from typing import Optional, List, Dict, Any
from enum import Enum
import json
import datetime
import sqlite3
import threading
from contextlib import contextmanager

# Configurar logging con mejor formato
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('memorae.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Importar configuración
try:
    from config import MODEL, DB_PATH, CREDENTIALS_PATH, EMAIL_SMTP, EMAIL_PORT, EMAIL_USER, EMAIL_PASS, WHATSAPP_NUMBER, GOOGLE_SPEECH_LANGUAGE
except ImportError as e:
    logger.error(f"Error importando configuración: {e}")
    raise

# Clases y enums para mejor organización
class TaskPriority(Enum):
    BAJA = "baja"
    MEDIA = "media"
    ALTA = "alta"

class ResponseType(Enum):
    RESPUESTA = "respuesta"
    TAREA = "tarea"
    LISTAR = "listar"
    COMPLETAR = "completar"
    RESUMEN = "resumen"

@dataclass
class Task:
    id: Optional[int] = None
    descripcion: str = ""
    fecha: str = ""
    prioridad: TaskPriority = TaskPriority.MEDIA
    completada: bool = False
    timestamp: str = ""

@dataclass
class Interaction:
    id: Optional[int] = None
    timestamp: str = ""
    usuario_input: str = ""
    agente_output: str = ""

class DatabaseManager:
    """Gestor de base de datos con contexto y mejor manejo de errores"""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self._lock = threading.Lock()
        self.init_db()
        self._lock = threading.Lock()
    
    @contextmanager
    def get_connection(self):
        """Context manager para conexiones a la base de datos"""
        conn = None
        try:
            with self._lock:
                conn = sqlite3.connect(self.db_path, timeout=10)
                conn.execute("PRAGMA foreign_keys = ON")
                yield conn
        except sqlite3.Error as e:
            logger.error(f"Error en base de datos: {e}")
            if conn:
                conn.rollback()
            raise
        finally:
            if conn:
                conn.close()

    def init_db(self):
        self._lock = threading.Lock()
        """Inicializar base de datos con mejor esquema"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Tabla historial mejorada
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS historial (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    usuario_input TEXT NOT NULL,
                    agente_output TEXT NOT NULL,
                    session_id TEXT,
                    tokens_used INTEGER DEFAULT 0
                )
            ''')
            
            # Tabla tareas mejorada
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS tareas (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    descripcion TEXT NOT NULL,
                    fecha DATETIME,
                    prioridad TEXT DEFAULT 'media' CHECK(prioridad IN ('baja', 'media', 'alta')),
                    completada BOOLEAN DEFAULT FALSE,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    categoria TEXT DEFAULT 'general',
                    notas TEXT
                )
            ''')
            
            # Índices para mejor rendimiento
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_historial_timestamp ON historial(timestamp)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_tareas_completada ON tareas(completada)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_tareas_prioridad ON tareas(prioridad)')
            
            conn.commit()

    def save_interaction(self, user_input: str, agent_output: str, session_id: str = None, tokens_used: int = 0) -> int:
        """Guardar interacción en base de datos"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            timestamp = datetime.datetime.now().isoformat()
            cursor.execute(
                'INSERT INTO historial (timestamp, usuario_input, agente_output, session_id, tokens_used) VALUES (?, ?, ?, ?, ?)',
                (timestamp, user_input, agent_output, session_id, tokens_used)
            )
            conn.commit()
            return cursor.lastrowid

    def get_recent_history(self, limit: int = 5) -> List[Interaction]:
        """Obtener historial reciente"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                'SELECT id, timestamp, usuario_input, agente_output FROM historial ORDER BY id DESC LIMIT ?',
                (limit,)
            )
            rows = cursor.fetchall()
            return [
                Interaction(id=row[0], timestamp=row[1], usuario_input=row[2], agente_output=row[3])
                for row in reversed(rows)
            ]

    def save_task(self, task: Task) -> int:
        """Guardar tarea en base de datos"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            if not task.timestamp:
                task.timestamp = datetime.datetime.now().isoformat()
            if not task.fecha:
                task.fecha = task.timestamp
            
            cursor.execute(
                'INSERT INTO tareas (descripcion, fecha, prioridad, timestamp, categoria, notas) VALUES (?, ?, ?, ?, ?, ?)',
                (task.descripcion, task.fecha, task.prioridad.value, task.timestamp, 'general', '')
            )
            conn.commit()
            return cursor.lastrowid

    def get_pending_tasks(self) -> List[Task]:
        """Obtener tareas pendientes"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                'SELECT id, descripcion, fecha, prioridad, completada, timestamp FROM tareas WHERE completada = FALSE ORDER BY fecha'
            )
            rows = cursor.fetchall()
            return [
                Task(
                    id=row[0],
                    descripcion=row[1],
                    fecha=row[2],
                    prioridad=TaskPriority(row[3]),
                    completada=row[4],
                    timestamp=row[5]
                )
                for row in rows
            ]

    def mark_task_completed(self, task_id: int) -> bool:
        """Marcar tarea como completada"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('UPDATE tareas SET completada = TRUE WHERE id = ?', (task_id,))
            conn.commit()
            return cursor.rowcount > 0

    def get_stats(self) -> Dict[str, Any]:
        """Obtener estadísticas de la base de datos"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            stats = {}
            
            # Estadísticas básicas
            cursor.execute('SELECT COUNT(*) FROM historial')
            stats['total_conversations'] = cursor.fetchone()[0]
            
            cursor.execute('SELECT COUNT(*) FROM tareas WHERE completada = FALSE')
            stats['pending_tasks'] = cursor.fetchone()[0]
            
            cursor.execute('SELECT COUNT(*) FROM tareas WHERE completada = TRUE')
            stats['completed_tasks'] = cursor.fetchone()[0]
            
            # Última interacción
            cursor.execute('SELECT timestamp FROM historial ORDER BY id DESC LIMIT 1')
            result = cursor.fetchone()
            stats['last_interaction'] = result[0] if result else "Nunca"
            
            # Estadísticas de tareas por prioridad
            cursor.execute('SELECT prioridad, COUNT(*) FROM tareas WHERE completada = FALSE GROUP BY prioridad')
            priority_stats = {row[0]: row[1] for row in cursor.fetchall()}
            stats['tasks_by_priority'] = priority_stats
            
            return stats

class VoiceManager:
    """Gestor de síntesis y reconocimiento de voz optimizado"""
    
    def __init__(self):
        self.engine = None
        self.recognizer = None
        self.voice_mode = None
        self._setup_voice()
    
    def _setup_voice(self):
        """Configurar sistema de voz con mejor manejo de errores"""
        try:
            import speech_recognition as sr
            self.recognizer = sr.Recognizer()
            logger.info("Reconocimiento de voz configurado.")
        except ImportError as e:
            logger.warning(f"Reconocimiento de voz no disponible: {e}")
        
        # Configurar síntesis de voz
        try:
            import pyttsx3
            self.engine = pyttsx3.init()
            self.voice_mode = 'pyttsx3'
            logger.info("pyttsx3 configurado exitosamente.")
        except Exception as e:
            logger.warning(f"pyttsx3 no disponible: {e}. Probando gTTS.")
            try:
                from gtts import gTTS
                import pygame
                import tempfile
                pygame.mixer.init()
                self.engine = {
                    'type': 'gtts',
                    'gtts': gTTS,
                    'pygame': pygame,
                    'temp_dir': tempfile.gettempdir()
                }
                self.voice_mode = 'gtts'
                logger.info("gTTS configurado como respaldo.")
            except Exception as gtts_e:
                logger.warning(f"Síntesis de voz no disponible: {gtts_e}")
                self.voice_mode = None
    
    def listen(self) -> Optional[str]:
        """Escuchar y reconocer voz"""
        if not self.recognizer:
            return None
            
        try:
            import speech_recognition as sr
            with sr.Microphone() as source:
                print("🎤 Escuchando...")
                self.recognizer.adjust_for_ambient_noise(source, duration=1)
                audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=10)
            
            text = self.recognizer.recognize_google(audio, language=GOOGLE_SPEECH_LANGUAGE)
            logger.info(f"Texto reconocido: {text}")
            return text
        except sr.WaitTimeoutError:
            logger.warning("Tiempo de espera agotado.")
        except sr.UnknownValueError:
            logger.warning("No se pudo entender el audio.")
        except Exception as e:
            logger.error(f"Error en reconocimiento de voz: {e}")
        
        return None
    
    def speak(self, text: str):
        """Sintetizar voz"""
        if not self.voice_mode:
            print(f"🤖 Memorae: {text}")
            return
        
        try:
            if self.voice_mode == 'pyttsx3':
                self.engine.say(text)
                self.engine.runAndWait()
            elif self.voice_mode == 'gtts':
                import os
                tts = self.engine['gtts'](text=text, lang='es')
                temp_file = os.path.join(self.engine['temp_dir'], 'temp_speech.mp3')
                tts.save(temp_file)
                self.engine['pygame'].mixer.music.load(temp_file)
                self.engine['pygame'].mixer.music.play()
                
                while self.engine['pygame'].mixer.music.get_busy():
                    self.engine['pygame'].time.wait(100)
                
                os.remove(temp_file)
                logger.info("Audio reproducido con gTTS.")
        except Exception as e:
            logger.error(f"Error en síntesis de voz: {e}")
            print(f"🤖 Memorae: {text}")

class LLMManager:
    """Gestor del modelo de lenguaje con mejor manejo de contexto"""
    
    def __init__(self, model: str = MODEL):
        self.model = model
        self._validate_model()
    
    def _validate_model(self):
        """Validar que el modelo esté disponible"""
        try:
            import ollama
            models = ollama.list()
            available_models = [m['name'] for m in models['models']]
            if self.model not in available_models:
                logger.warning(f"Modelo {self.model} no encontrado. Modelos disponibles: {available_models}")
        except Exception as e:
            logger.error(f"Error validando modelo: {e}")
    
    def generate_response(self, user_input: str, context: List[Interaction]) -> str:
        """Generar respuesta usando el LLM"""
        try:
            import ollama
            
            # Construir contexto
            context_str = "\n".join([
                f"Usuario: {interaction.usuario_input}\nAsistente: {interaction.agente_output}"
                for interaction in context
            ])
            
            # Prompt optimizado
            prompt = self._build_prompt(user_input, context_str)
            
            logger.info(f"Generando respuesta para: {user_input[:50]}...")
            response = ollama.chat(
                model=self.model,
                messages=[{'role': 'user', 'content': prompt}],
                options={'temperature': 0.7, 'top_p': 0.9}
            )
            
            result = response['message']['content']
            logger.info("Respuesta generada exitosamente.")
            return result
            
        except Exception as e:
            logger.error(f"Error generando respuesta: {e}")
            return "Lo siento, hay un problema con el procesamiento. Intenta de nuevo."
    
    def _build_prompt(self, user_input: str, context: str) -> str:
        """Construir prompt optimizado"""
        return f"""Eres Memorae, un asistente AI personal inteligente y útil. Tu objetivo es ayudar al usuario con sus tareas diarias, recordatorios y preguntas.

CONTEXTO DE LA CONVERSACIÓN:
{context}

INSTRUCCIONES:
- Responde en español de forma natural y conversacional
- Si detectas una solicitud de tarea/recordatorio, responde con JSON: {{"tipo": "tarea", "descripcion": "...", "prioridad": "baja/media/alta", "fecha": "YYYY-MM-DDTHH:MM"}}
- Si piden listar tareas: {{"tipo": "listar"}}
- Si piden completar una tarea: {{"tipo": "completar", "id": número}}
- Para respuestas normales, responde directamente sin JSON
- Sé proactivo y ofrece ayuda adicional cuando sea apropiado

CONSULTA ACTUAL: {user_input}

RESPUESTA:"""

class NotificationManager:
    """Gestor de notificaciones y integraciones externas"""
    
    def __init__(self):
        self.available_services = self._check_services()
    
    def _check_services(self) -> Dict[str, bool]:
        """Verificar servicios disponibles"""
        services = {}
        
        # Verificar notificaciones locales
        try:
            from plyer import notification
            services['local_notifications'] = True
        except ImportError:
            services['local_notifications'] = False
        
        # Verificar WhatsApp
        try:
            import pywhatkit as pwk
            services['whatsapp'] = os.environ.get('DISPLAY') is not None
        except ImportError:
            services['whatsapp'] = False
        
        # Verificar email
        services['email'] = bool(EMAIL_USER and EMAIL_PASS)
        
        logger.info(f"Servicios disponibles: {services}")
        return services
    
    def send_notification(self, title: str, message: str, service: str = 'local'):
        """Enviar notificación"""
        try:
            if service == 'local' and self.available_services.get('local_notifications'):
                from plyer import notification
                notification.notify(title=title, message=message, timeout=10)
                logger.info(f"Notificación local enviada: {title}")
                
            elif service == 'email' and self.available_services.get('email'):
                self._send_email(title, message)
                
            elif service == 'whatsapp' and self.available_services.get('whatsapp'):
                self._send_whatsapp(message)
                
        except Exception as e:
            logger.error(f"Error enviando notificación: {e}")
    
    def _send_email(self, subject: str, body: str):
        """Enviar email"""
        try:
            import smtplib
            from email.mime.text import MIMEText
            
            msg = MIMEText(body)
            msg['Subject'] = subject
            msg['From'] = EMAIL_USER
            msg['To'] = EMAIL_USER  # Enviar a uno mismo por defecto
            
            with smtplib.SMTP(EMAIL_SMTP, EMAIL_PORT) as server:
                server.starttls()
                server.login(EMAIL_USER, EMAIL_PASS)
                server.sendmail(EMAIL_USER, [EMAIL_USER], msg.as_string())
            
            logger.info("Email enviado exitosamente.")
        except Exception as e:
            logger.error(f"Error enviando email: {e}")
    
    def _send_whatsapp(self, message: str):
        """Enviar WhatsApp"""
        try:
            import pywhatkit as pwk
            pwk.sendwhatmsg_instantly(WHATSAPP_NUMBER, message)
            logger.info("Mensaje WhatsApp enviado.")
        except Exception as e:
            logger.error(f"Error enviando WhatsApp: {e}")

class MemoraeCLI:
    """Interfaz de línea de comandos mejorada para Memorae"""
    
    def __init__(self):
        self.db_manager = DatabaseManager(DB_PATH)
        self.voice_manager = VoiceManager()
        self.llm_manager = LLMManager()
        self.notification_manager = NotificationManager()
        self.session_id = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        
    def run(self):
        """Ejecutar el asistente"""
        logger.info("🚀 Iniciando Memorae CLI optimizado")
        
        # Mostrar información inicial
        stats = self.db_manager.get_stats()
        print(f"""
🤖 Memorae - Asistente AI Personal
{'='*40}
💬 Conversaciones: {stats['total_conversations']}
📋 Tareas pendientes: {stats['pending_tasks']}
✅ Tareas completadas: {stats['completed_tasks']}
🤖 Modelo: {MODEL}
{'='*40}
""")
        
        # Configurar modo de voz
        use_voice = self._ask_voice_mode()
        
        try:
            while True:
                try:
                    # Obtener entrada del usuario
                    if use_voice and self.voice_manager.recognizer:
                        user_input = self.voice_manager.listen()
                        if user_input and 'salir' in user_input.lower():
                            break
                        if not user_input:
                            continue
                        print(f"👤 Tú: {user_input}")
                    else:
                        user_input = input("👤 Tú: ").strip()
                        if user_input.lower() in ['salir', 'exit', 'quit']:
                            break
                        if not user_input:
                            continue
                    
                    # Procesar entrada
                    response = self._process_input(user_input)
                    
                    # Mostrar respuesta
                    print(f"🤖 Memorae: {response}")
                    
                    # Síntesis de voz si está habilitada
                    if use_voice:
                        self.voice_manager.speak(response)
                        
                except KeyboardInterrupt:
                    print("\n\n👋 Interrupción detectada. ¡Hasta luego!")
                    break
                except EOFError:
                    print("\n\n👋 Fin de entrada detectado. ¡Hasta luego!")
                    break
                except Exception as e:
                    logger.error(f"Error en el bucle principal: {e}")
                    print(f"❌ Error: {e}")
                    
        except Exception as e:
            logger.error(f"Error crítico: {e}")
        finally:
            print("👋 ¡Hasta luego! Memorae se está cerrando...")
    
    def _ask_voice_mode(self) -> bool:
        """Preguntar si usar modo voz"""
        try:
            if not self.voice_manager.recognizer:
                print("🔇 Modo voz no disponible (falta micrófono o dependencias)")
                return False
            
            response = input("🎤 ¿Usar modo voz? (s/n): ").lower()
            return response in ['s', 'si', 'sí', 'y', 'yes']
        except (EOFError, KeyboardInterrupt):
            print("Usando modo texto por defecto.")
            return False
    
    def _process_input(self, user_input: str) -> str:
        """Procesar entrada del usuario"""
        # Obtener contexto
        context = self.db_manager.get_recent_history(limit=5)
        
        # Generar respuesta
        llm_response = self.llm_manager.generate_response(user_input, context)
        
        # Procesar respuesta
        processed_response = self._handle_response(llm_response, user_input)
        
        # Guardar interacción
        self.db_manager.save_interaction(user_input, processed_response, self.session_id)
        
        return processed_response
    
    def _handle_response(self, llm_response: str, user_input: str) -> str:
        """Manejar respuesta del LLM"""
        try:
            # Intentar parsear como JSON
            if llm_response.strip().startswith('{'):
                parsed = json.loads(llm_response)
                return self._handle_structured_response(parsed)
            else:
                return llm_response
        except json.JSONDecodeError:
            return llm_response
    
    def _handle_structured_response(self, parsed: Dict[str, Any]) -> str:
        """Manejar respuesta estructurada"""
        response_type = parsed.get('tipo', 'respuesta')
        
        if response_type == 'tarea':
            return self._handle_task_creation(parsed)
        elif response_type == 'listar':
            return self._handle_task_listing()
        elif response_type == 'completar':
            return self._handle_task_completion(parsed)
        else:
            return parsed.get('contenido', str(parsed))
    
    def _handle_task_creation(self, data: Dict[str, Any]) -> str:
        """Manejar creación de tarea"""
        try:
            task = Task(
                descripcion=data.get('descripcion', ''),
                prioridad=TaskPriority(data.get('prioridad', 'media')),
                fecha=data.get('fecha')
            )
            
            task_id = self.db_manager.save_task(task)
            
            # Enviar notificación
            self.notification_manager.send_notification(
                "Nueva Tarea", 
                f"Tarea creada: {task.descripcion}"
            )
            
            return f"✅ Tarea creada (ID: {task_id}): {task.descripcion} - Prioridad: {task.prioridad.value}"
            
        except Exception as e:
            logger.error(f"Error creando tarea: {e}")
            return f"❌ Error creando tarea: {e}"
    
    def _handle_task_listing(self) -> str:
        """Manejar listado de tareas"""
        try:
            tasks = self.db_manager.get_pending_tasks()
            if not tasks:
                return "📝 No hay tareas pendientes."
            
            task_list = []
            for task in tasks:
                task_list.append(f"• [{task.id}] {task.descripcion} ({task.prioridad.value})")
            
            return f"📋 Tareas pendientes ({len(tasks)}):\n" + "\n".join(task_list)
            
        except Exception as e:
            logger.error(f"Error listando tareas: {e}")
            return f"❌ Error listando tareas: {e}"
    
    def _handle_task_completion(self, data: Dict[str, Any]) -> str:
        """Manejar completado de tarea"""
        try:
            task_id = data.get('id')
            if not task_id:
                return "❌ ID de tarea no especificado."
            
            success = self.db_manager.mark_task_completed(int(task_id))
            if success:
                self.notification_manager.send_notification(
                    "Tarea Completada", 
                    f"Tarea {task_id} marcada como completada"
                )
                return f"✅ Tarea {task_id} marcada como completada."
            else:
                return f"❌ No se encontró la tarea {task_id}."
                
        except Exception as e:
            logger.error(f"Error completando tarea: {e}")
            return f"❌ Error completando tarea: {e}"

def main():
    """Función principal"""
    try:
        cli = MemoraeCLI()
        cli.run()
    except Exception as e:
        logger.error(f"Error crítico en main: {e}")
        print(f"💥 Error crítico: {e}")

if __name__ == "__main__":
    main()

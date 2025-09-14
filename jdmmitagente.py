#!/usr/bin/env python3
"""
JDMMitAgente - Asistente Inteligente Optimizado
Versión 3.0.0 - Optimizado con MySQL y funcionalidades mejoradas
"""

import os
import sys
import logging
from datetime import datetime, timedelta
import json
import uuid

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('jdmmitagente.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger('JDMMitAgente')

# Verificar disponibilidad de display para GUI
PWK_AVAILABLE = os.environ.get('DISPLAY') is not None
if not PWK_AVAILABLE:
    logger.warning("No hay display gráfico disponible. Funcionalidades GUI limitadas.")

# Importaciones principales
try:
    from config import (
        MODEL, DB_CONFIG, EMAIL_SMTP, EMAIL_PORT, EMAIL_USER, EMAIL_PASS,
        WHATSAPP_NUMBER, GOOGLE_SPEECH_LANGUAGE, ASSISTANT_NAME, 
        ASSISTANT_VERSION, OLLAMA_HOST
    )
except ImportError as e:
    logger.error(f"Error importando configuraciones: {e}")
    sys.exit(1)

# Importaciones de dependencias
import mysql.connector
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import ollama
from plyer import notification

# Importaciones opcionales
try:
    if PWK_AVAILABLE:
        import pywhatkit as pwk
    else:
        pwk = None
except ImportError as e:
    logger.warning(f"PyWhatKit no disponible: {e}")
    pwk = None

try:
    import speech_recognition as sr
    import pyttsx3
    VOICE_AVAILABLE = True
except ImportError as e:
    logger.warning(f"Funcionalidades de voz no disponibles: {e}")
    VOICE_AVAILABLE = False
    sr = None
    pyttsx3 = None

try:
    from gtts import gTTS
    import pygame
    import tempfile
    GTTS_AVAILABLE = True
except ImportError:
    logger.warning("gTTS no disponible como fallback")
    GTTS_AVAILABLE = False


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
            cursor = self.connection.cursor(dictionary=True)
            cursor.execute(query, params or ())
            
            if fetch:
                result = cursor.fetchall()
                cursor.close()
                return result
            else:
                self.connection.commit()
                cursor.close()
                return True
                
        except mysql.connector.Error as e:
            logger.error(f"Error ejecutando query: {e}")
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


class VoiceManager:
    """Gestor de funcionalidades de voz optimizado"""
    
    def __init__(self):
        self.engine = None
        self.recognizer = None
        self.voice_mode = None
        self.setup_voice()
    
    def setup_voice(self):
        """Configurar sistema de voz con fallbacks"""
        if not VOICE_AVAILABLE:
            logger.warning("Funcionalidades de voz no disponibles")
            return
        
        # Configurar reconocimiento de voz
        try:
            self.recognizer = sr.Recognizer()
            self.recognizer.energy_threshold = 300
            self.recognizer.dynamic_energy_threshold = True
            logger.info("Reconocimiento de voz configurado")
        except Exception as e:
            logger.error(f"Error configurando reconocimiento: {e}")
        
        # Configurar síntesis de voz - Intentar pyttsx3 primero
        try:
            self.engine = pyttsx3.init()
            self.voice_mode = 'pyttsx3'
            # Configurar propiedades de voz
            voices = self.engine.getProperty('voices')
            if voices:
                # Buscar voz en español si está disponible
                for voice in voices:
                    if 'spanish' in voice.name.lower() or 'es' in voice.id.lower():
                        self.engine.setProperty('voice', voice.id)
                        break
            self.engine.setProperty('rate', 180)  # Velocidad de habla
            self.engine.setProperty('volume', 0.8)  # Volumen
            logger.info("pyttsx3 configurado exitosamente")
        except Exception as e:
            logger.warning(f"pyttsx3 falló: {e}, intentando gTTS")
            if GTTS_AVAILABLE:
                try:
                    pygame.mixer.init()
                    self.engine = 'gtts'
                    self.voice_mode = 'gtts'
                    logger.info("gTTS configurado como fallback")
                except Exception as gtts_e:
                    logger.error(f"gTTS también falló: {gtts_e}")
                    self.voice_mode = None
    
    def listen(self, timeout=5):
        """Escuchar entrada de voz"""
        if not self.recognizer:
            return None
        
        try:
            with sr.Microphone() as source:
                print("🎤 Escuchando...")
                self.recognizer.adjust_for_ambient_noise(source, duration=1)
                audio = self.recognizer.listen(source, timeout=timeout)
            
            print("🔍 Procesando...")
            text = self.recognizer.recognize_google(audio, language=GOOGLE_SPEECH_LANGUAGE)
            logger.info(f"Texto reconocido: {text}")
            return text
            
        except sr.WaitTimeoutError:
            print("⏱️ Tiempo de espera agotado")
            return None
        except sr.UnknownValueError:
            print("❌ No se pudo entender el audio")
            return None
        except Exception as e:
            logger.error(f"Error en reconocimiento de voz: {e}")
            return None
    
    def speak(self, text):
        """Síntesis de voz"""
        if self.voice_mode == 'pyttsx3':
            try:
                self.engine.say(text)
                self.engine.runAndWait()
            except Exception as e:
                logger.error(f"Error con pyttsx3: {e}")
                print(f"🤖 {text}")
        
        elif self.voice_mode == 'gtts':
            try:
                tts = gTTS(text=text, lang='es')
                temp_file = os.path.join(tempfile.gettempdir(), 'jdmmitagente_speech.mp3')
                tts.save(temp_file)
                pygame.mixer.music.load(temp_file)
                pygame.mixer.music.play()
                while pygame.mixer.music.get_busy():
                    pygame.time.wait(100)
                os.remove(temp_file)
            except Exception as e:
                logger.error(f"Error con gTTS: {e}")
                print(f"🤖 {text}")
        else:
            print(f"🤖 {text}")


class CommunicationManager:
    """Gestor de comunicaciones (email, WhatsApp, notificaciones)"""
    
    @staticmethod
    def send_email(to_email, subject, body, html_body=None):
        """Enviar email"""
        try:
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = EMAIL_USER
            msg['To'] = to_email
            
            # Agregar contenido de texto
            text_part = MIMEText(body, 'plain')
            msg.attach(text_part)
            
            # Agregar contenido HTML si se proporciona
            if html_body:
                html_part = MIMEText(html_body, 'html')
                msg.attach(html_part)
            
            server = smtplib.SMTP(EMAIL_SMTP, EMAIL_PORT)
            server.starttls()
            server.login(EMAIL_USER, EMAIL_PASS)
            server.send_message(msg)
            server.quit()
            
            logger.info(f"Email enviado exitosamente a {to_email}")
            return True, "Email enviado exitosamente"
        except Exception as e:
            logger.error(f"Error enviando email: {e}")
            return False, f"Error enviando email: {e}"
    
    @staticmethod
    def send_whatsapp(phone_number, message):
        """Enviar mensaje de WhatsApp"""
        if not PWK_AVAILABLE or not pwk:
            return False, "WhatsApp no disponible (requiere GUI)"
        
        try:
            phone_number = phone_number or WHATSAPP_NUMBER
            pwk.sendwhatmsg_instantly(phone_number, message)
            logger.info("Mensaje WhatsApp enviado")
            return True, "Mensaje WhatsApp enviado"
        except Exception as e:
            logger.error(f"Error enviando WhatsApp: {e}")
            return False, f"Error WhatsApp: {e}"
    
    @staticmethod
    def send_notification(title, message, timeout=10):
        """Enviar notificación local"""
        try:
            notification.notify(title=title, message=message, timeout=timeout)
            return True, "Notificación enviada"
        except Exception as e:
            logger.error(f"Error enviando notificación: {e}")
            return False, f"Error notificación: {e}"


class OllamaManager:
    """Gestor de interacciones con Ollama"""
    
    def __init__(self):
        self.client = ollama.Client(host=OLLAMA_HOST)
        self.model = MODEL
        self.test_connection()
    
    def test_connection(self):
        """Probar conexión con Ollama"""
        try:
            models = self.client.list()
            logger.info(f"Conectado a Ollama. Modelos disponibles: {len(models.get('models', []))}")
        except Exception as e:
            logger.error(f"Error conectando a Ollama: {e}")
            raise
    
    def chat(self, message, context=None):
        """Chatear con el modelo"""
        try:
            # Construir contexto si se proporciona
            if context:
                context_text = "\n".join([
                    f"Usuario: {c['user_message']}\nAsistente: {c['assistant_message']}" 
                    for c in context
                ])
                system_prompt = f"""Eres {ASSISTANT_NAME}, un asistente inteligente en español.
Contexto de conversaciones previas:
{context_text}

Instrucciones:
- Responde en español de manera natural y útil
- Para tareas, recordatorios o eventos, responde en JSON:
  {{"tipo": "tarea", "titulo": "...", "descripcion": "...", "fecha": "YYYY-MM-DD HH:MM", "prioridad": "baja/media/alta"}}
- Para listar tareas: {{"tipo": "listar_tareas"}}
- Para completar tarea: {{"tipo": "completar_tarea", "id": 1}}
- Para guardar información importante: {{"tipo": "memoria", "categoria": "...", "info": "...", "detalles": "..."}}
- Para respuestas normales, solo texto natural
"""
            else:
                system_prompt = f"Eres {ASSISTANT_NAME}, un asistente inteligente que responde en español de manera útil y natural."
            
            response = self.client.chat(
                model=self.model,
                messages=[
                    {'role': 'system', 'content': system_prompt},
                    {'role': 'user', 'content': message}
                ]
            )
            
            return response['message']['content']
            
        except Exception as e:
            logger.error(f"Error en chat con Ollama: {e}")
            return "Disculpa, hay un problema técnico. Intenta de nuevo."


class JDMMitAgente:
    """Clase principal del asistente JDMMitAgente"""
    
    def __init__(self):
        self.db = DatabaseManager()
        self.voice = VoiceManager()
        self.comm = CommunicationManager()
        self.ollama = OllamaManager()
        self.session_id = str(uuid.uuid4())
        logger.info(f"{ASSISTANT_NAME} v{ASSISTANT_VERSION} inicializado")
    
    def process_response(self, response):
        """Procesar respuesta del LLM y determinar acciones"""
        try:
            # Intentar parsear JSON
            if response.strip().startswith('{') and response.strip().endswith('}'):
                return json.loads(response.strip())
            else:
                return {'tipo': 'respuesta', 'contenido': response}
        except json.JSONDecodeError:
            return {'tipo': 'respuesta', 'contenido': response}
    
    def handle_task(self, task_data):
        """Manejar creación de tarea"""
        titulo = task_data.get('titulo', 'Tarea sin título')
        descripcion = task_data.get('descripcion', '')
        fecha_str = task_data.get('fecha', '')
        prioridad = task_data.get('prioridad', 'media')
        
        # Parsear fecha si se proporciona
        fecha = None
        if fecha_str:
            try:
                fecha = datetime.strptime(fecha_str, '%Y-%m-%d %H:%M')
            except ValueError:
                try:
                    fecha = datetime.strptime(fecha_str, '%Y-%m-%d')
                except ValueError:
                    fecha = datetime.now() + timedelta(hours=1)  # Default 1 hora
        else:
            fecha = datetime.now() + timedelta(hours=1)
        
        # Guardar tarea
        success = self.db.save_task(titulo, descripcion, fecha)
        if success:
            # Enviar notificación
            self.comm.send_notification("Nueva Tarea", f"{titulo} - {descripcion}")
            return f"✅ Tarea guardada: {titulo} para {fecha.strftime('%Y-%m-%d %H:%M')}"
        else:
            return "❌ Error guardando la tarea"
    
    def handle_list_tasks(self):
        """Listar tareas pendientes"""
        tasks = self.db.get_pending_tasks()
        if not tasks:
            return "📋 No tienes tareas pendientes"
        
        response = "📋 Tus tareas pendientes:\n\n"
        for task in tasks:
            fecha = task['scheduled_time'].strftime('%Y-%m-%d %H:%M')
            response += f"• ID {task['id']}: {task['task_name']}\n"
            response += f"  📅 {fecha}\n"
            response += f"  📝 {task['description']}\n\n"
        
        return response
    
    def handle_complete_task(self, task_id):
        """Completar tarea"""
        success = self.db.complete_task(task_id)
        if success:
            return f"✅ Tarea {task_id} completada"
        else:
            return f"❌ Error completando tarea {task_id}"
    
    def handle_memory(self, memory_data):
        """Guardar información en memoria"""
        categoria = memory_data.get('categoria', 'general')
        info = memory_data.get('info', '')
        detalles = memory_data.get('detalles', '')
        
        success = self.db.save_memory(categoria, info, detalles)
        if success:
            return f"🧠 Información guardada en memoria (categoría: {categoria})"
        else:
            return "❌ Error guardando información"
    
    def run_interactive(self):
        """Ejecutar modo interactivo"""
        print(f"🤖 {ASSISTANT_NAME} v{ASSISTANT_VERSION} listo!")
        print("💡 Comandos especiales: 'voz' (activar/desactivar), 'salir' (terminar)")
        
        voice_mode = False
        
        # Preguntar por modo de voz si está disponible
        if self.voice.voice_mode:
            try:
                voice_input = input("¿Activar modo voz? (s/n): ").lower()
                voice_mode = voice_input in ['s', 'si', 'sí', 'yes', 'y']
            except (EOFError, KeyboardInterrupt):
                pass
        
        while True:
            try:
                # Obtener entrada del usuario
                if voice_mode and self.voice.voice_mode:
                    user_input = self.voice.listen()
                    if not user_input:
                        continue
                    print(f"👤 {user_input}")
                else:
                    user_input = input("\n👤 Tú: ").strip()
                
                if not user_input:
                    continue
                
                # Comandos especiales
                if user_input.lower() in ['salir', 'exit', 'quit']:
                    break
                elif user_input.lower() == 'voz':
                    voice_mode = not voice_mode
                    status = "activado" if voice_mode else "desactivado"
                    print(f"🎤 Modo voz {status}")
                    continue
                
                # Obtener contexto de conversaciones recientes
                context = self.db.get_recent_conversations()
                
                # Procesar con Ollama
                response = self.ollama.chat(user_input, context)
                parsed_response = self.process_response(response)
                
                # Manejar diferentes tipos de respuesta
                if parsed_response['tipo'] == 'tarea':
                    output = self.handle_task(parsed_response)
                elif parsed_response['tipo'] == 'listar_tareas':
                    output = self.handle_list_tasks()
                elif parsed_response['tipo'] == 'completar_tarea':
                    task_id = parsed_response.get('id')
                    output = self.handle_complete_task(task_id)
                elif parsed_response['tipo'] == 'memoria':
                    output = self.handle_memory(parsed_response)
                else:
                    output = parsed_response.get('contenido', response)
                
                # Mostrar respuesta
                print(f"🤖 {output}")
                
                # Hablar si está en modo voz
                if voice_mode and self.voice.voice_mode:
                    self.voice.speak(output)
                
                # Guardar conversación
                self.db.save_conversation(user_input, output, self.session_id)
                
            except (EOFError, KeyboardInterrupt):
                print("\n👋 ¡Hasta luego!")
                break
            except Exception as e:
                logger.error(f"Error en bucle principal: {e}")
                print("❌ Error procesando tu solicitud")
    
    def run_command(self, command):
        """Ejecutar comando único"""
        context = self.db.get_recent_conversations()
        response = self.ollama.chat(command, context)
        parsed_response = self.process_response(response)
        
        if parsed_response['tipo'] == 'tarea':
            output = self.handle_task(parsed_response)
        elif parsed_response['tipo'] == 'listar_tareas':
            output = self.handle_list_tasks()
        elif parsed_response['tipo'] == 'completar_tarea':
            task_id = parsed_response.get('id')
            output = self.handle_complete_task(task_id)
        elif parsed_response['tipo'] == 'memoria':
            output = self.handle_memory(parsed_response)
        else:
            output = parsed_response.get('contenido', response)
        
        print(output)
        self.db.save_conversation(command, output, self.session_id)


def main():
    """Función principal"""
    import argparse
    
    parser = argparse.ArgumentParser(description=f'{ASSISTANT_NAME} v{ASSISTANT_VERSION}')
    parser.add_argument('--command', '-c', help='Ejecutar comando único')
    parser.add_argument('--gui', action='store_true', help='Iniciar interfaz gráfica (próximamente)')
    
    args = parser.parse_args()
    
    try:
        agent = JDMMitAgente()
        
        if args.command:
            agent.run_command(args.command)
        elif args.gui:
            print("🚧 Interfaz gráfica en desarrollo")
        else:
            agent.run_interactive()
            
    except KeyboardInterrupt:
        print("\n👋 ¡Hasta luego!")
    except Exception as e:
        logger.error(f"Error fatal: {e}")
        print(f"❌ Error fatal: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

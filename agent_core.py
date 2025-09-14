
import logging
import json
import uuid
import re
from datetime import datetime, timedelta

from database_manager import DatabaseManager
from voice_manager import VoiceManager
from communication_manager import CommunicationManager
from ollama_manager import OllamaManager
from config import ASSISTANT_NAME, ASSISTANT_VERSION
from constants import (
    ACTION_TASK, ACTION_LIST_TASKS, ACTION_COMPLETE_TASK, 
    ACTION_MEMORY, ACTION_RESPONSE
)

logger = logging.getLogger(__name__)

class JDMMitAgente:
    """Clase principal del asistente JDMMitAgente, ahora modularizada"""

    def __init__(self):
        try:
            self.db = DatabaseManager()
            self.voice = VoiceManager()
            self.comm = CommunicationManager()
            self.ollama = OllamaManager()
            self.session_id = str(uuid.uuid4())
            logger.info(f"{ASSISTANT_NAME} v{ASSISTANT_VERSION} inicializado con éxito.")
        except Exception as e:
            logger.critical(f"Error fatal durante la inicialización del agente: {e}", exc_info=True)
            raise

    def process_response(self, response: str):
        """
        Procesa la respuesta del LLM para determinar la acción a tomar.
        Busca y extrae un bloque JSON de la respuesta, incluso si está rodeado de texto.
        """
        try:
            # Primero, busca un bloque de código JSON (```json ... ```)
            match = re.search(r"```json\s*({.*?})\s*```", response, re.DOTALL)
            if match:
                json_str = match.group(1)
                return json.loads(json_str)

            # Si no, busca el primer '{' y el último '}' como un fallback.
            start_index = response.find('{')
            end_index = response.rfind('}')
            if start_index != -1 and end_index != -1 and start_index < end_index:
                json_str = response[start_index:end_index+1]
                return json.loads(json_str)
            
            logger.info(f"La respuesta no contenía un JSON válido. Tratando como texto: {response}")

        except json.JSONDecodeError as e:
            logger.warning(f"No se pudo decodificar el JSON extraído de la respuesta: {response}. Error: {e}")
        
        # Si todo lo demás falla, devuelve una acción de respuesta simple.
        return {'tipo': ACTION_RESPONSE, 'contenido': response}

    def _try_parse_date(self, date_str):
        """Intenta parsear una fecha desde varios formatos comunes."""
        formats = [
            '%Y-%m-%d %H:%M:%S', '%Y-%m-%d %H:%M', '%Y-%m-%d',
            '%d/%m/%Y %H:%M:%S', '%d/%m/%Y %H:%M', '%d/%m/%Y',
        ]
        for fmt in formats:
            try:
                return datetime.strptime(date_str, fmt)
            except (ValueError, TypeError):
                continue
        return None

    def _handle_task(self, task_data):
        """Maneja la creación y guardado de una nueva tarea"""
        titulo = task_data.get('titulo', 'Tarea sin título')
        descripcion = task_data.get('descripcion', '')
        fecha_str = task_data.get('fecha')

        if fecha_str:
            fecha = self._try_parse_date(fecha_str)
            if not fecha:
                logger.warning(f"Formato de fecha inválido: {fecha_str}. Usando fecha por defecto.")
                fecha = datetime.now() + timedelta(minutes=10)
        else:
            fecha = datetime.now() + timedelta(minutes=10)

        if self.db.save_task(titulo, descripcion, fecha):
            self.comm.send_notification("Nueva Tarea Guardada", f"{titulo} a las {fecha.strftime('%H:%M')}")
            return f"✅ Tarea guardada: '{titulo}' para el {fecha.strftime('%Y-%m-%d a las %H:%M')}."
        else:
            return "❌ Lo siento, no pude guardar la tarea en la base de datos."

    def _handle_list_tasks(self):
        """Maneja la solicitud de listar tareas pendientes"""
        tasks = self.db.get_pending_tasks()
        if not tasks:
            return "📋 No tienes ninguna tarea pendiente en este momento."

        response = "📋 Aquí están tus tareas pendientes:\n\n"
        for task in tasks:
            fecha = task['scheduled_time'].strftime('%d de %b a las %H:%M')
            response += f"- **ID {task['id']}**: {task['task_name']} (Para: {fecha})\n"
            if task['description']:
                response += f"  - _{task['description']}_\n"
        return response

    def _handle_complete_task(self, task_id):
        """Maneja la solicitud de completar una tarea"""
        if not task_id:
            return "🤔 Necesito el ID de la tarea que quieres completar."
        if self.db.complete_task(task_id):
            return f"✅ ¡Perfecto! He marcado la tarea {task_id} como completada."
        else:
            return f"❌ No pude marcar la tarea {task_id} como completada. Verifica el ID."

    def _handle_memory(self, memory_data):
        """Maneja el guardado de información en la memoria a largo plazo"""
        categoria = memory_data.get('categoria', 'general')
        info = memory_data.get('info')
        detalles = memory_data.get('detalles', '')

        if not info:
            return "🤔 No me diste la información clave para guardar en la memoria."

        if self.db.save_memory(categoria, info, detalles):
            return f"🧠 He guardado la siguiente información en la categoría '{categoria}': '{info}'"
        else:
            return "❌ No pude guardar la información en la memoria."

    def execute_command(self, command):
        """Ejecuta un comando (sin cerrar la sesión) y devuelve el resultado."""
        context = self.db.get_recent_conversations()
        response_llm = self.ollama.chat(command, context)
        parsed_response = self.process_response(response_llm)
        output = self._execute_action(parsed_response)
        self.db.save_conversation(command, output, self.session_id)
        return output

    def run_single_command(self, command):
        """Ejecuta un solo comando y termina la sesión."""
        output = self.execute_command(command)
        print(output)
        self.shutdown()

    def run_interactive_mode(self):
        """Ejecuta el asistente en modo interactivo de consola"""
        print(f"\n🤖 {ASSISTANT_NAME} v{ASSISTANT_VERSION} está listo para ayudarte.")
        print("💡 Escribe 'salir' para terminar o 'voz' para activar/desactivar el modo de voz.")
        
        voice_mode = False

        while True:
            try:
                if voice_mode and self.voice.voice_mode:
                    user_input = self.voice.listen()
                    if not user_input:
                        continue
                    print(f"\n👤 (Voz) Tú: {user_input}")
                else:
                    user_input = input("\n👤 Tú: ").strip()

                if not user_input:
                    continue

                if user_input.lower() in ['salir', 'exit', 'quit']:
                    break
                if user_input.lower() == 'voz':
                    if self.voice.voice_mode:
                        voice_mode = not voice_mode
                        status = "activado" if voice_mode else "desactivado"
                        print(f"🎤 El modo de voz ha sido {status}.")
                        self.voice.speak(f"Modo voz {status}")
                    else:
                        print("🎤 El módulo de voz no está disponible en este sistema.")
                    continue

                output = self.execute_command(user_input)

                print(f"🤖 {output}")
                if voice_mode:
                    self.voice.speak(output)

            except (KeyboardInterrupt, EOFError):
                break
            except Exception as e:
                logger.error(f"Ha ocurrido un error en el bucle principal: {e}", exc_info=True)
                print("💥 Oops! Algo salió mal. Por favor, intenta de nuevo.")

        self.shutdown()

    def _execute_action(self, parsed_response):
        """Ejecuta la acción determinada a partir de la respuesta parseada del LLM"""
        action_map = {
            ACTION_TASK: self._handle_task,
            ACTION_LIST_TASKS: lambda data: self._handle_list_tasks(),
            ACTION_COMPLETE_TASK: lambda data: self._handle_complete_task(data.get('id')),
            ACTION_MEMORY: self._handle_memory,
        }

        action_type = parsed_response.get('tipo')
        handler = action_map.get(action_type)

        if handler:
            return handler(parsed_response)
        elif action_type == ACTION_RESPONSE:
            return parsed_response.get('contenido', "No he podido procesar la respuesta.")
        else:
            logger.warning(f"Tipo de acción no reconocido: {action_type}")
            return parsed_response.get('contenido', "No estoy seguro de cómo procesar eso.")

    def shutdown(self):
        """Cierra las conexiones y recursos del agente"""
        print("\n👋 ¡Hasta luego! Cerrando el asistente.")
        self.db.close()

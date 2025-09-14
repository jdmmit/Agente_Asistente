
import logging
import json
import uuid
import re
from datetime import datetime, timedelta

from database_manager import DatabaseManager
from voice_manager import VoiceManager
# Quitamos la importación directa de CommunicationManager para la carga diferida
# from communication_manager import CommunicationManager 
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
            self.ollama = OllamaManager()
            self.session_id = str(uuid.uuid4())
            # Inicializamos el gestor de comunicación como None. Se cargará cuando sea necesario.
            self.comm = None 
            logger.info(f"{ASSISTANT_NAME} v{ASSISTANT_VERSION} inicializado con éxito.")
        except Exception as e:
            logger.critical(f"Error fatal durante la inicialización del agente: {e}", exc_info=True)
            raise

    def _get_comm_manager(self):
        """
        Importa e inicializa CommunicationManager solo cuando se necesita (carga diferida).
        Esto evita errores de importación en entornos sin GUI (ej. para pruebas).
        """
        # Si ya está cargado, lo devolvemos
        if self.comm:
            return self.comm
        
        try:
            # Este es el único lugar donde se importa CommunicationManager
            from communication_manager import CommunicationManager
            self.comm = CommunicationManager()
            logger.info("CommunicationManager cargado dinámicamente.")
        except Exception as e:
            logger.warning(f"No se pudo cargar CommunicationManager (puede ser normal en un entorno sin GUI). Las notificaciones estarán desactivadas. Error: {e}")
            # Creamos un objeto "falso" para evitar que el resto del código falle
            class DummyCommManager:
                def send_notification(self, *args, **kwargs):
                    logger.warning("Intento de enviar notificación, pero CommunicationManager no está disponible.")
                    pass # No hacer nada
            self.comm = DummyCommManager()
        
        return self.comm

    def process_response(self, response: str):
        """
        Procesa la respuesta del LLM para determinar la acción a tomar.
        """
        try:
            match = re.search(r"```json\s*({.*?})\s*```", response, re.DOTALL)
            if match:
                json_str = match.group(1)
                return json.loads(json_str)

            start_index = response.find('{')
            end_index = response.rfind('}')
            if start_index != -1 and end_index != -1 and start_index < end_index:
                json_str = response[start_index:end_index+1]
                return json.loads(json_str)
            
            logger.info(f"La respuesta no contenía un JSON válido. Tratando como texto: {response}")

        except json.JSONDecodeError as e:
            logger.warning(f"No se pudo decodificar el JSON: {e}")
        
        return {'tipo': ACTION_RESPONSE, 'contenido': response}

    def _try_parse_date(self, date_str):
        formats = ['%Y-%m-%d %H:%M:%S', '%Y-%m-%d %H:%M', '%Y-%m-%d', '%d/%m/%Y %H:%M:%S', '%d/%m/%Y %H:%M', '%d/%m/%Y']
        for fmt in formats:
            try: return datetime.strptime(date_str, fmt)
            except (ValueError, TypeError): continue
        return None

    def _handle_task(self, task_data):
        titulo = task_data.get('titulo', 'Tarea sin título')
        descripcion = task_data.get('descripcion', '')
        fecha_str = task_data.get('fecha')
        fecha = self._try_parse_date(fecha_str) if fecha_str else datetime.now() + timedelta(minutes=10)

        if self.db.save_task(titulo, descripcion, fecha):
            # Obtenemos el gestor de comunicación justo antes de usarlo
            comm_manager = self._get_comm_manager()
            comm_manager.send_notification("Nueva Tarea Guardada", f"{titulo} a las {fecha.strftime('%H:%M')}")
            return f"✅ Tarea guardada: '{titulo}' para el {fecha.strftime('%Y-%m-%d a las %H:%M')}."
        else:
            return "❌ Lo siento, no pude guardar la tarea."

    def _handle_list_tasks(self):
        tasks = self.db.get_pending_tasks()
        if not tasks: return "📋 No tienes ninguna tarea pendiente."
        response = "📋 Aquí están tus tareas pendientes:\n\n"
        for task in tasks:
            fecha = task['scheduled_time'].strftime('%d de %b a las %H:%M')
            response += f"- **ID {task['id']}**: {task['task_name']} (Para: {fecha})\n"
        return response

    def _handle_complete_task(self, task_id):
        if not task_id: return "🤔 Necesito el ID de la tarea a completar."
        if self.db.complete_task(task_id): return f"✅ ¡Perfecto! Tarea {task_id} completada."
        else: return f"❌ No pude marcar la tarea {task_id} como completada."

    def _handle_memory(self, memory_data):
        categoria = memory_data.get('categoria', 'general')
        info = memory_data.get('info')
        if not info: return "🤔 No me diste la información clave para guardar."
        if self.db.save_memory(categoria, info, memory_data.get('detalles', '')):
            return f"🧠 He guardado en '{categoria}': '{info}'"
        else: return "❌ No pude guardar la información."

    def execute_command(self, command):
        context = self.db.get_recent_conversations()
        response_llm = self.ollama.chat(command, context)
        parsed_response = self.process_response(response_llm)
        output = self._execute_action(parsed_response)
        self.db.save_conversation(command, output, self.session_id)
        return output

    def run_interactive_mode(self):
        print(f"\n🤖 {ASSISTANT_NAME} v{ASSISTANT_VERSION} está listo.")
        print("💡 Escribe 'salir' para terminar.")
        voice_mode = False
        while True:
            try:
                user_input = input("\n👤 Tú: ").strip()
                if not user_input: continue
                if user_input.lower() in ['salir', 'exit', 'quit']: break
                output = self.execute_command(user_input)
                print(f"🤖 {output}")
            except (KeyboardInterrupt, EOFError): break
            except Exception as e:
                logger.error(f"Error en el bucle principal: {e}", exc_info=True)
                print("💥 Oops! Algo salió mal.")
        self.shutdown()

    def _execute_action(self, parsed_response):
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
        print("\n👋 ¡Hasta luego! Cerrando el asistente.")
        self.db.close()

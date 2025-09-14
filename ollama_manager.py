
import logging
import ollama

from config import MODEL, OLLAMA_HOST, ASSISTANT_NAME

logger = logging.getLogger(__name__)


class OllamaManager:
    """Gestor de interacciones con Ollama"""

    def __init__(self):
        self.model = MODEL
        try:
            self.client = ollama.Client(host=OLLAMA_HOST)
            self.test_connection()
        except Exception as e:
            logger.error(f"No se pudo conectar con el cliente de Ollama en {OLLAMA_HOST}. Error: {e}")
            raise

    def test_connection(self):
        """Verifica la conexión con el servidor de Ollama y la existencia del modelo"""
        try:
            models = self.client.list()['models']
            model_names = [m['name'] for m in models]
            logger.info(f"Conexión a Ollama exitosa. Modelos disponibles: {model_names}")
            
            if self.model not in model_names:
                logger.warning(f"El modelo '{self.model}' no está disponible en Ollama. Intentando hacer 'pull'...")
                self.pull_model(self.model)

        except Exception as e:
            logger.error(f"Error conectando a Ollama en {OLLAMA_HOST}: {e}")
            raise

    def pull_model(self, model_name):
        """Descarga un modelo de Ollama si no existe"""
        try:
            logger.info(f"Descargando el modelo '{model_name}'. Esto puede tardar...")
            self.client.pull(model_name)
            logger.info(f"Modelo '{model_name}' descargado exitosamente.")
        except Exception as e:
            logger.error(f"No se pudo descargar el modelo '{model_name}': {e}")
            raise

    def chat(self, message, context=None):
        """Chatear con el modelo, incluyendo contexto y un prompt de sistema robusto"""
        system_prompt = self._build_system_prompt(context)
        messages = [
            {'role': 'system', 'content': system_prompt},
            {'role': 'user', 'content': message}
        ]

        try:
            response = self.client.chat(model=self.model, messages=messages)
            content = response['message']['content']
            logger.debug(f"Respuesta completa de Ollama: {content}")
            return content

        except Exception as e:
            logger.error(f"Error en la llamada a Ollama: {e}")
            return "Disculpa, he encontrado un problema técnico al procesar tu solicitud. Por favor, inténtalo de nuevo."

    def _build_system_prompt(self, context):
        """Construye el prompt de sistema dinámicamente"""
        context_text = ""
        if context:
            context_text = "\n".join([
                f"Usuario: {c['user_message']}\nAsistente: {c['assistant_message']}"
                for c in context
            ])

        prompt = f"""Eres {ASSISTANT_NAME}, un asistente personal inteligente y proactivo que habla español.

Contexto de la conversación reciente (si lo hay):
{context_text}

== INSTRUCCIONES ==
1.  **Rol Principal**: Tu objetivo es ayudar al usuario con sus tareas, recordatorios, gestión de información y responder a sus preguntas de forma clara y concisa.
2.  **Análisis de Intención**: Analiza la entrada del usuario para identificar la acción principal que desea realizar (crear tarea, listar, buscar, etc.).
3.  **Formato de Salida**: Debes responder en uno de los siguientes formatos JSON o como texto plano, según corresponda.

    *   **Crear Tarea/Recordatorio**: Si el usuario quiere agendar algo.
        ```json
        {{
            "tipo": "tarea",
            "titulo": "<título conciso de la tarea>",
            "descripcion": "<descripción detallada si es necesario>",
            "fecha": "<YYYY-MM-DD HH:MM en formato 24h>",
            "prioridad": "<baja/media/alta>"
        }}
        ```
        -   **Importante**: La fecha debe ser inferida del texto del usuario (ej. "mañana a las 10am", "el viernes"). Si no se especifica, usa la fecha y hora actual.

    *   **Listar Tareas**: Si el usuario pide ver sus tareas pendientes.
        ```json
        {{"tipo": "listar_tareas"}}
        ```

    *   **Completar Tarea**: Si el usuario indica que ha finalizado una tarea.
        ```json
        {{"tipo": "completar_tarea", "id": <número_del_ID_de_la_tarea>}}
        ```

    *   **Guardar en Memoria**: Si el usuario te pide que recuerdes algo importante.
        ```json
        {{
            "tipo": "memoria",
            "categoria": "<categoría general, ej: personal, trabajo, proyecto_x>",
            "info": "<la información clave a recordar>",
            "detalles": "<detalles adicionales>"
        }}
        ```

    *   **Respuesta General**: Para cualquier otra consulta (preguntas, saludos, etc.), responde como texto plano, sin formato JSON. Sé amable y natural.

4.  **Idioma**: Responde siempre en español.
"""
        return prompt



#!/usr/bin/env python3
"""
JDMMitAgente - API del Asistente Inteligente
Versión 3.0.0 - Refactorizado y Modularizado

Este script expone la funcionalidad del agente a través de una API REST.
"""

import logging
import sys
from flask import Flask, request, jsonify
from agent_core import JDMMitAgente
from config import LOG_FILE

# --- Configuración del Logging --- #
log_level = logging.INFO
log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
handlers = [
    logging.FileHandler(LOG_FILE),
    logging.StreamHandler(sys.stdout)
]
logging.basicConfig(level=log_level, format=log_format, handlers=handlers)
logger = logging.getLogger(__name__)

# --- Inicialización de la Aplicación Flask y el Agente --- #
app = Flask(__name__)
agent = None

def initialize_agent():
    """Inicializa la instancia del agente."""
    global agent
    if agent is None:
        try:
            agent = JDMMitAgente()
            logger.info("Instancia de JDMMitAgente creada con éxito.")
        except Exception as e:
            logger.critical(f"Error fatal al inicializar JDMMitAgente: {e}", exc_info=True)
            # Esto podría causar que la app no inicie, lo cual es deseable si el agente no puede funcionar.
            raise
    return agent

# --- Definición de Rutas de la API --- #
@app.route('/api/command', methods=['POST'])
def handle_command():
    """
    Maneja la ejecución de un único comando recibido vía POST.
    Espera un JSON con la clave 'prompt'.
    """
    logger.debug("Recibida solicitud en /api/command")
    
    if not request.is_json:
        logger.warning("Solicitud recibida no es de tipo JSON.")
        return jsonify({"error": "La solicitud debe ser de tipo application/json"}), 415

    data = request.get_json()
    prompt = data.get('prompt')

    if not prompt:
        logger.warning("No se encontró 'prompt' en el cuerpo de la solicitud.")
        return jsonify({"error": "El cuerpo de la solicitud debe contener la clave 'prompt'"}), 400

    try:
        agente_local = initialize_agent()
        logger.info(f"Ejecutando comando a través de la API: '{prompt}'")
        # Aquí asumimos que run_single_command devuelve un string con la respuesta.
        # Si devuelve otro formato, habría que ajustarlo.
        response = agente_local.run_single_command(prompt)
        logger.info(f"Respuesta generada: {response}")
        return jsonify({"response": response})

    except Exception as e:
        logger.error(f"Error al procesar el comando: {e}", exc_info=True)
        return jsonify({"error": "Se ha producido un error interno al procesar el comando."}), 500

# --- Punto de Entrada Principal --- #
if __name__ == "__main__":
    # Asegurarse de que el agente se inicializa al arrancar
    try:
        initialize_agent()
        logger.info(f"Servidor API para JDMMitAgente iniciando...")
        # Escuchar en todas las interfaces en el puerto 5000 (puerto por defecto de Flask)
        # Es crucial usar 0.0.0.0 para que sea accesible desde otros contenedores Docker.
        app.run(host='0.0.0.0', port=5000)
    except Exception as e:
        logger.critical(f"No se pudo iniciar el servidor API: {e}", exc_info=True)
        sys.exit(1)

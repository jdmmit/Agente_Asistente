
#!/usr/bin/env python3
"""
JDMMitAgente - Asistente Inteligente
Versión 3.0.0 - Refactorizado y Modularizado

Este script es el punto de entrada para iniciar el asistente.
"""

import logging
import sys
import argparse
import subprocess

from config import ASSISTANT_NAME, ASSISTANT_VERSION, LOG_FILE
from agent_core import JDMMitAgente

# --- Configuración del Logging --- #
log_level = logging.INFO
log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
handlers = [
    logging.FileHandler(LOG_FILE),
    logging.StreamHandler(sys.stdout)
]
logging.basicConfig(
    level=log_level,
    format=log_format,
    handlers=handlers
)
logger = logging.getLogger(__name__)


# --- Función Principal --- #
def main():
    """Punto de entrada principal del programa."""
    
    parser = argparse.ArgumentParser(
        description=f"{ASSISTANT_NAME} v{ASSISTANT_VERSION} - Tu Asistente Inteligente",
        epilog="Ejecuta sin argumentos para iniciar en modo interactivo."
    )
    
    parser.add_argument(
        '-c', '--command',
        type=str,
        help='Ejecuta un único comando y sale.'
    )
    parser.add_argument(
        '--web',
        action='store_true',
        help='Inicia la interfaz gráfica web con Streamlit.'
    )
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Activa el logging detallado (DEBUG).'
    )

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
        logger.debug("Logging en modo DEBUG activado.")

    if args.web:
        logger.info("Iniciando la interfaz web con Streamlit...")
        try:
            subprocess.run(["streamlit", "run", "streamlit_app.py"], check=True)
        except FileNotFoundError:
            logger.error("El comando 'streamlit' no fue encontrado. Asegúrate de que Streamlit está instalado y en tu PATH.")
            print("Error: 'streamlit' no encontrado. Por favor, instala Streamlit con 'pip install streamlit'.")
        except Exception as e:
            logger.critical(f"No se pudo iniciar la aplicación Streamlit: {e}", exc_info=True)
        return

    try:
        agent = JDMMitAgente()

        if args.command:
            logger.info(f"Ejecutando comando único: '{args.command}'")
            agent.run_single_command(args.command)
        else:
            logger.info("Iniciando en modo interactivo...")
            agent.run_interactive_mode()

    except KeyboardInterrupt:
        print("\n\nPrograma interrumpido por el usuario. ¡Adiós!")
    except Exception as e:
        logger.critical(f"Error fatal al ejecutar el agente: {e}", exc_info=True)
        print(f"💥 Se ha producido un error fatal. Revisa el archivo de log '{LOG_FILE}' para más detalles.")
        sys.exit(1)


if __name__ == "__main__":
    main()

# Guía de Despliegue con Docker para Memorae

Esta guía detalla cómo ejecutar el proyecto en contenedores Docker con Docker Compose. Esto proporciona aislamiento, persistencia para Ollama (modelos LLM) y acceso a internet para APIs (email, Calendar, gTTS) y conexiones locales (ports para GUI).

## Prerrequisitos

- Docker y Docker Compose instalados.
  - Linux (Ubuntu/Debian): `sudo apt update && sudo apt install docker.io docker-compose`.
  - Verifica: `docker --version` y `docker-compose --version`.
  - Agrega usuario a grupo docker: `sudo usermod -aG docker $USER` (logout/login para aplicar).
  - Si persiste permiso denegado, usa `sudo` temporalmente para comandos docker.
- Directorio del proyecto: `/home/ctrl/git_hub/Agente_Asistente`.

## Paso 1: Preparar Configuraciones Locales

1. Ejecuta el setup: `python setup_config.py` (genera .env con email, WhatsApp, modelo, etc.).
2. Coloca `credentials.json` (para Google Calendar) en el directorio del proyecto.
3. Asegúrate de que .gitignore excluya .env (ya incluido).

## Paso 2: Build y Run

1. En terminal del proyecto: `docker-compose up --build`.

   - **Primera vez**:
     - Build de imagen 'app' (instala dependencias Python).
     - Ollama se inicia y descarga modelo 'llama3' (~4.7GB, requiere internet; puede tomar tiempo).
     - Logs muestran "Ollama ready" y app iniciando en CLI mode.
   - **Ejecución**:
     - App corre en CLI (interactúa via logs; para input, usa `docker-compose exec app python agente.py`).
     - Ollama accesible en http://localhost:11434 (API local).
   - Para background: `docker-compose up -d --build`.

2. **Acceso a GUI**:
   - CLI: Logs en terminal o `docker-compose logs -f app`.
   - GUI Tkinter: `docker-compose run --rm app python agente.py --gui` (abre ventana; para remote, configura X11 forwarding: `docker run -e DISPLAY=$DISPLAY -v /tmp/.X11-unix:/tmp/.X11-unix`).
   - GUI Streamlit: `docker-compose run

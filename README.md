# Memorae - Tu Asistente de IA Local y Personal

![Memorae Banner](https://i.imgur.com/example.png) <!-- Reemplazar con un banner real -->

Memorae es un asistente inteligente diseñado para funcionar localmente en tu máquina. Te ayuda a organizar tu día, gestionar tareas, recordar información importante y mucho más, todo mientras mantiene tu información completamente privada y bajo tu control.

---

## 📝 Índice

1.  [✨ Características Principales](#-características-principales)
2.  [🚀 Cómo Funciona](#-cómo-funciona)
3.  [🔧 Instalación y Ejecución](#-instalación-y-ejecución)
    *   [Método 1: Docker (Recomendado)](#método-1-docker-recomendado)
    *   [Método 2: Local (Para Desarrollo)](#método-2-local-para-desarrollo)
4.  [▶️ Cómo Usar Memorae](#️-cómo-usar-memorae)
5.  [💬 Comandos del Asistente](#-comandos-del-asistente)

---

## ✨ Características Principales

*   **100% Local y Privado**: Tus datos nunca salen de tu máquina. Utiliza [Ollama](https://ollama.com/) para ejecutar modelos de lenguaje grandes (LLMs) de forma local.
*   **Gestión de Tareas**: Crea, lista y completa tareas usando lenguaje natural.
*   **Memoria a Largo Plazo**: Pídele a Memorae que recuerde información importante por ti.
*   **Múltiples Interfaces**: Úsalo a través de una interfaz web amigable o directamente desde tu terminal.
*   **Fácil de Instalar**: Métodos de instalación claros y sencillos con Docker o un script local.

---

## 🚀 Cómo Funciona

Memorae utiliza una arquitectura modular para ser flexible y potente. El núcleo del agente (`agent_core.py`) procesa tus solicitudes, se comunica con el modelo de lenguaje de Ollama (`ollama_manager.py`) para entenderte y gestiona tus datos a través de un manejador de base de datos (`database_manager.py`).

---

## 🔧 Instalación y Ejecución

### Prerrequisitos

*   **Generales**: Git para clonar el repositorio.
*   **Para Docker**: [Docker](https://docs.docker.com/get-docker/) y Docker Compose instalados.
*   **Para la instalación local**: Python 3.10+ y `python3-venv`.
*   **Ollama**: Debes tener Ollama instalado y corriendo. Sigue las instrucciones en [ollama.com](https://ollama.com/download).
    *   Una vez instalado, descarga un modelo. Recomendamos `llama3`:
      ```bash
      ollama pull llama3
      ```

### Método 1: Docker (Recomendado)

Este es el método más sencillo y robusto. Docker se encarga de todo el entorno por ti.

1.  **Clona el repositorio** e ingresa al directorio:
    ```bash
    git clone https://github.com/tu-usuario/jdm-mit-agente.git
    cd jdm-mit-agente
    ```
    *(Reemplaza la URL con la URL real del repositorio cuando esté disponible)*

2.  **Construye y levanta los servicios** con Docker Compose:
    ```bash
    docker compose up --build
    ```

¡Eso es todo! La aplicación (interfaz web y agente) se iniciará automáticamente. Puedes acceder a la interfaz web en `http://localhost:8501`.

### Método 2: Local (Para Desarrollo)

Ideal si quieres modificar el código, probar cambios rápidamente o no quieres usar Docker.

1.  **Clona el repositorio** e ingresa al directorio (si aún no lo has hecho).

2.  **Ejecuta el script de instalación local**:
    ```bash
    sh install-local.sh
    ```
    Este script creará un entorno virtual de Python, instalará todas las dependencias necesarias y te guiará para crear un archivo de configuración `.env` para tus datos sensibles.

---

## ▶️ Cómo Usar Memorae

Una vez instalado y en ejecución, puedes interactuar con Memorae de dos maneras:

### Interfaz Web (Streamlit)

*   **Si usaste Docker**: La interfaz está disponible automáticamente en `http://localhost:8501`.
*   **Si usaste el método local**: El script `install-local.sh` te habrá dado la opción de iniciar la interfaz web al finalizar. Si no, puedes iniciarla manualmente (asegúrate de que el entorno virtual esté activado):
    ```bash
    # Activa el entorno virtual si no lo está
    source .venv/bin/activate
    # Lanza la app de Streamlit
    streamlit run streamlit_app.py
    ```

### Modo Interactivo (Terminal)

Perfecto para una experiencia de línea de comandos.

*   **Si usaste el método local**, puedes iniciar el modo interactivo así (asegúrate de que el entorno virtual esté activado):
    ```bash
    # Activa el entorno virtual si no lo está
    source .venv/bin/activate
    # Ejecuta el agente en modo terminal
    python jdmmitagente.py
    ```

---

## 💬 Comandos del Asistente

Habla con Memorae usando lenguaje natural. Aquí tienes algunos ejemplos de lo que puedes pedirle.

### Crear una Tarea

> "Recuérdame que tengo que llamar al banco mañana a las 10 de la mañana"
> "Añade una tarea para comprar el pan, con descripción 'comprar dos barras'"

### Listar Tareas

> "¿Qué tareas tengo pendientes?"
> "Muéstrame mi lista de tareas"

### Completar una Tarea

Necesitarás el ID que te da el asistente al listar las tareas.

> "Ya terminé la tarea con ID 3"
> "Completar la tarea 5"

### Guardar en la Memoria

> "Recuerda que mi número de vuelo para el viaje es el AV-456"
> "Guarda en la categoría 'trabajo' que el jefe de proyecto se llama Carlos"

### Conversación General

> "Hola, ¿cómo estás?"
> "¿Cuál es la capital de Mongolia?"

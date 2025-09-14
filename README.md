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
5.  [🧪 Pruebas](#-pruebas)
6.  [💬 Comandos del Asistente](#-comandos-del-asistente)

---

## ✨ Características Principales

*   **100% Local y Privado**: Tus datos nunca salen de tu máquina. Utiliza [Ollama](https://ollama.com/) para ejecutar modelos de lenguaje grandes (LLMs) de forma local.
*   **Gestión de Tareas**: Crea, lista y completa tareas usando lenguaje natural.
*   **Memoria a Largo Plazo**: Pídele a Memorae que recuerde información importante por ti.
*   **Múltiples Interfaces**: Úsalo a través de una interfaz web amigable o directamente desde tu terminal.
*   **Fácil de Instalar**: Un único script de instalación te guía para usar Docker o configurar un entorno local.

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

### Proceso de Instalación

1.  **Clona el repositorio** e ingresa al directorio:
    ```bash
    git clone https://github.com/tu-usuario/jdm-mit-agente.git
    cd jdm-mit-agente
    ```
    *(Reemplaza la URL con la URL real del repositorio cuando esté disponible)*

2.  **Ejecuta el script de instalación principal**:
    ```bash
    sh install.sh
    ```

3.  **Sigue las instrucciones del menú**: El script te permitirá elegir entre:
    *   **Instalación con Docker (Recomendada)**: Automáticamente construirá y lanzará los contenedores. La forma más fácil de empezar.
    *   **Instalación Local**: Creará un entorno virtual, instalará dependencias y te guiará para configurar el archivo `.env`.

---

## ▶️ Cómo Usar Memorae

Una vez instalado, puedes interactuar con Memorae de dos maneras:

### Interfaz Web (Streamlit)

*   **Si usaste Docker**: La interfaz está disponible automáticamente en `http://localhost:8501`.
*   **Si usaste el método local**: El script de instalación te habrá dado la opción de iniciar la interfaz web al finalizar. Si no, puedes iniciarla manualmente (asegúrate de que el entorno virtual esté activado):
    ```bash
    # Activa el entorno virtual si no lo está
    source .venv/bin/activate
    # Lanza la app de Streamlit
    streamlit run streamlit_app.py
    ```

### Modo Interactivo (Terminal)

*   **Si usaste el método local**, puedes iniciar el modo interactivo así (asegúrate de que el entorno virtual esté activado):
    ```bash
    # Activa el entorno virtual si no lo está
    source .venv/bin/activate
    # Ejecuta el agente en modo terminal
    python jdmmitagente.py
    ```

---

## 🧪 Pruebas

Para asegurar la calidad y estabilidad del código, el proyecto incluye un conjunto de pruebas automatizadas. Estas pruebas verifican la conexión a la base de datos, la lógica del agente y la interacción con los diferentes módulos.

Para ejecutar las pruebas:

1.  Asegúrate de haber completado la **instalación local** primero, ya que las pruebas dependen del entorno virtual creado.

2.  Ejecuta el script de pruebas:
    ```bash
    sh run-tests.sh
    ```

El script mostrará los resultados de cada prueba. Un resultado exitoso es esencial para confirmar que los cambios recientes no han roto ninguna funcionalidad clave.

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

# Memorae - Tu Asistente de IA Local y Personal

![Memorae Banner](https://i.imgur.com/example.png) <!-- Reemplazar con un banner real -->

Memorae es un asistente inteligente diseñado para funcionar localmente en tu máquina. Te ayuda a organizar tu día, gestionar tareas, recordar información importante y mucho más, todo mientras mantiene tu información completamente privada y bajo tu control.

---

## 📝 Índice

1.  [✨ Características Principales](#-características-principales)
2.  [🚀 Cómo Funciona](#-cómo-funciona)
3.  [🔧 Instalación](#-instalación)
    *   [Opción 1: Instalación Automática con Docker (Recomendado)](#opción-1-instalación-automática-con-docker-recomendado)
    *   [Opción 2: Instalación Local (Para Desarrolladores)](#opción-2-instalación-local-para-desarrolladores)
4.  [▶️ Cómo Usar Memorae](#️-cómo-usar-memorae)
    *   [Interfaz Web (Streamlit)](#interfaz-web-streamlit)
    *   [Modo Interactivo (Terminal)](#modo-interactivo-terminal)
5.  [💬 Comandos del Asistente](#-comandos-del-asistente)
    *   [Crear una Tarea](#crear-una-tarea)
    *   [Listar Tareas](#listar-tareas)
    *   [Completar una Tarea](#completar-una-tarea)
    *   [Guardar en la Memoria](#guardar-en-la-memoria)
    *   [Conversación General](#conversación-general)

---

## ✨ Características Principales

*   **100% Local y Privado**: Tus datos nunca salen de tu máquina. Utiliza [Ollama](https://ollama.com/) para ejecutar modelos de lenguaje grandes (LLMs) de forma local.
*   **Gestión de Tareas**: Crea, lista y completa tareas usando lenguaje natural.
*   **Memoria a Largo Plazo**: Pídele a Memorae que recuerde información importante por ti.
*   **Múltiples Interfaces**: Úsalo a través de una interfaz web amigable o directamente desde tu terminal.
*   **Notificaciones**: Recibe alertas sobre tus tareas (próximamente).
*   **Fácil de Instalar**: Un único script se encarga de toda la configuración inicial.

---

## 🚀 Cómo Funciona

Memorae utiliza una arquitectura modular para ser flexible y potente. El núcleo del agente (`agent_core.py`) procesa tus solicitudes, se comunica con el modelo de lenguaje de Ollama (`ollama_manager.py`) para entenderte y gestiona tus datos a través de un manejador de base de datos (`database_manager.py`).

---

## 🔧 Instalación

### Prerrequisitos

*   **Para la instalación con Docker**: Necesitas tener [Docker](https://docs.docker.com/get-docker/) y Docker Compose instalados.
*   **Para la instalación local**: Necesitas Python 3.8+, pip y Git.
*   **Ollama**: Debes tener Ollama instalado. Sigue las instrucciones en [ollama.com](https://ollama.com/download).
    *   Una vez instalado, descarga un modelo. Recomendamos `llama3`:
      ```bash
      ollama pull llama3
      ```

### Opción 1: Instalación Automática con Docker (Recomendado)

Este es el método más sencillo. Un único script se encarga de todo.

1.  **Clona el repositorio**:
    ```bash
    git clone <URL-del-repositorio>
    cd <nombre-del-repositorio>
    ```

2.  **Ejecuta el script de instalación**:
    ```bash
    ./install.sh
    ```

    El script te guiará para:
    *   Instalar las dependencias de Python.
    *   Configurar de forma segura tus datos sensibles (email, etc.) en un archivo `.env`.
    *   Construir e iniciar los contenedores de Docker.

¡Y eso es todo! La interfaz web estará disponible en `http://localhost:8501`.

### Opción 2: Instalación Local (Para Desarrolladores)

Ideal si quieres modificar el código.

1.  **Clona el repositorio y entra en el directorio** (si aún no lo has hecho).

2.  **Ejecuta el script de configuración segura**:
    ```bash
    chmod +x utils/secure-env.sh
    ./utils/secure-env.sh
    ```
    Este script instalará las dependencias y te ayudará a crear tu archivo `.env`.

---

## ▶️ Cómo Usar Memorae

### Interfaz Web (Streamlit)

Si usaste la instalación con Docker o `install.sh`, la interfaz web ya debería estar corriendo. Si la instalación fue local, ejecútala con:

```bash
streamlit run streamlit_app.py
```

Abre tu navegador y ve a `http://localhost:8501`.

### Modo Interactivo (Terminal)

Para una experiencia clásica en la línea de comandos:

```bash
python jdmmitagente.py
```

---

## 💬 Comandos del Asistente

Habla con Memorae usando lenguaje natural. Aquí tienes algunos ejemplos de lo que puedes pedirle.

### Crear una Tarea

Pídele que agende algo por ti. Puedes ser tan específico como quieras.

> "Recuérdame que tengo que llamar al banco mañana a las 10 de la mañana"

> "Añade una tarea para comprar el pan, con descripción 'comprar dos barras'"

El asistente entiende fechas relativas ("mañana", "el viernes que viene") y horas.

### Listar Tareas

Revisa lo que tienes pendiente.

> "¿Qué tareas tengo pendientes?"

> "Muéstrame mi lista de tareas"

### Completar una Tarea

Cuando termines algo, solo díselo. Necesitarás el ID que te da el asistente al listar las tareas.

> "Ya terminé la tarea con ID 3"

> "Completar la tarea 5"

### Guardar en la Memoria

Pídele que recuerde datos, hechos o cualquier cosa que necesites.

> "Recuerda que mi número de vuelo para el viaje es el AV-456"

> "Guarda en la categoría 'trabajo' que el jefe de proyecto se llama Carlos"

### Conversación General

También puedes hablar con él, hacerle preguntas o simplemente saludar.

> "Hola, ¿cómo estás?"

> "¿Cuál es la capital de Mongolia?"

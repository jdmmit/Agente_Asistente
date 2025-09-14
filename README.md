# Configurador de Usuario y Verificador de WhatsApp con Chat Llama 3

Este proyecto proporciona una interfaz web simple con dos funcionalidades principales:
1.  **Configurador de Usuario**: Permite configurar datos de usuario y verificar una conexión con la API de WhatsApp de Twilio enviando un mensaje de prueba.
2.  **Chat con Llama 3**: Ofrece una interfaz de chat para interactuar con el modelo de lenguaje Llama 3, que se ejecuta localmente a través de Ollama.

La aplicación está completamente contenedorizada con Docker, lo que garantiza una instalación y ejecución sencillas.

---

## 🚀 Cómo Funciona

La aplicación utiliza Streamlit para crear la interfaz web. Al rellenar y enviar el formulario de configuración, la aplicación usa las credenciales de Twilio para enviar un mensaje de prueba.

Paralelamente, la aplicación incluye una sección de chat que se conecta a un servicio de Ollama que se ejecuta en un contenedor Docker separado. Esto te permite chatear con el modelo Llama 3 directamente desde la interfaz.

---

## ⚙️ Configuración Obligatoria: Credenciales de Twilio

Antes de poder usar el verificador de WhatsApp, es **esencial** que configures tus credenciales de Twilio.

1.  **Crea un Archivo de Secretos**:
    Dentro del proyecto, crea un directorio llamado `.streamlit` si no existe. Dentro de él, crea un archivo llamado `secrets.toml`.

2.  **Añade tus Credenciales**:
    Copia y pega lo siguiente en tu archivo `.streamlit/secrets.toml` y rellénalo con tus datos de [la consola de Twilio](https://www.twilio.com/console).

    ```toml
    # Tu Account SID de Twilio.
    TWILIO_ACCOUNT_SID = "ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"

    # Tu Auth Token de Twilio.
    TWILIO_AUTH_TOKEN = "tu_auth_token_aqui"

    # Tu número de teléfono de Twilio con capacidad para WhatsApp.
    TWILIO_PHONE_NUMBER = "whatsapp:+15017122661"
    ```

    > **⚠️ Importante sobre el Sandbox de Twilio**: Si usas el sandbox, asegúrate de haber vinculado tu número de WhatsApp al sandbox enviando el mensaje de activación (ej: `join company-slug`) al número del sandbox.

---

## ▶️ Ejecución con Docker (Recomendado)

La forma más sencilla de ejecutar todo el sistema, incluido el chat con Llama 3.

### Prerrequisitos

*   **Docker y Docker Compose**: La forma más fácil es usar [Docker Desktop](https://www.docker.com/products/docker-desktop/).
*   **Git**: Para clonar el repositorio.

### Pasos

1.  **Clona el repositorio**:
    ```bash
    git clone https://github.com/jdmmit/Agente_Asistente.git
    cd Agente_Asistente
    ```

2.  **Levanta la aplicación y el servicio de Ollama**:
    ```bash
    docker compose up --build
    ```

3.  **Descarga el modelo Llama 3 (en una nueva terminal)**:
    Mientras los contenedores se ejecutan, abre una nueva terminal y ejecuta el siguiente comando para que el servicio de Ollama descargue el modelo Llama 3.
    ```bash
    docker exec -it ollama_service ollama pull llama3
    ```
    > **Nota**: Este paso solo es necesario la primera vez. El modelo se guardará en un volumen de Docker y estará disponible en futuros inicios.

4.  **Accede a la Interfaz**:
    Abre tu navegador y dirígete a `http://localhost:8501`.

---

## ▶️ Ejecución en Local (Sin Docker)

Si prefieres no usar Docker, puedes ejecutar la aplicación de Streamlit directamente. **Nota**: Este método no incluye la ejecución del modelo Llama 3, ya que requiere una instalación local de Ollama.

### Prerrequisitos

*   **Python 3.8+** y **pip**.
*   **Git**.

### Pasos

1.  **Clona el repositorio** y entra en el directorio.

2.  **Crea y activa un entorno virtual**:
    ```bash
    python3 -m venv .venv
    source .venv/bin/activate
    ```

3.  **Instala las dependencias**:
    ```bash
    pip install -r requirements.txt
    ```

4.  **Ejecuta la aplicación**:
    ```bash
    streamlit run streamlit_app.py
    ```

5.  **Accede a la Interfaz**:
    Abre tu navegador y dirígete a la URL que te indique la terminal.

---

## 📝 Uso de la Aplicación

*   **Para verificar WhatsApp**: Rellena el formulario y haz clic en "Guardar y Enviar Mensaje de Prueba".
*   **Para chatear con Llama 3**: Desplázate hacia abajo hasta la sección de chat, escribe tu pregunta y presiona Enter.

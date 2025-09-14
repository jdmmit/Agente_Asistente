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

## ⚙️ Configuración Manual: Credenciales de Twilio

Para que la aplicación pueda enviar mensajes a través de WhatsApp, es **esencial** que configures tus credenciales de Twilio. Sigue estos pasos:

### Paso 1: Ve a la carpeta raíz de tu proyecto

Abre una terminal y asegúrate de estar en el directorio principal del proyecto (la misma carpeta donde se encuentra el archivo `docker-compose.yml`).

### Paso 2: Crea el directorio `.streamlit`

Si este directorio no existe, créalo con el siguiente comando. Si ya existe, puedes omitir este paso.

```bash
mkdir .streamlit
```

### Paso 3: Crea tu archivo de secretos

Crea el archivo que guardará tus credenciales. Puedes usar la plantilla que he incluido en el repositorio para que sea más fácil:

```bash
cp .streamlit/secrets.toml.template .streamlit/secrets.toml
```

### Paso 4: Añade tus credenciales al archivo

Abre el archivo `.streamlit/secrets.toml` con tu editor de código favorito y verás el siguiente contenido:

```toml
# Credenciales de Twilio
# Reemplaza los valores con tus credenciales reales de la consola de Twilio.

# Tu Account SID de Twilio.
TWILIO_ACCOUNT_SID = "ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"

# Tu Auth Token de Twilio.
TWILIO_AUTH_TOKEN = "tu_auth_token_aqui"

# Tu número de teléfono de Twilio con capacidad para WhatsApp.
# Debe tener el formato: whatsapp:+CODIGO_PAISNUMERO
TWILIO_PHONE_NUMBER = "whatsapp:+15017122661"
```

### Paso 5: Rellena con tus credenciales reales

Reemplaza los valores de ejemplo con tus credenciales, que puedes encontrar en [la consola de Twilio](https://www.twilio.com/console).

*   **`ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`**: Reemplázalo con tu **Account SID**.
*   **`tu_auth_token_aqui`**: Reemplázalo con tu **Auth Token**.
*   **`whatsapp:+15017122661`**: Reemplázalo con tu **número de teléfono de Twilio para WhatsApp**.

> **⚠️ Importante sobre el Sandbox de Twilio**: Si usas el sandbox, asegúrate de haber vinculado tu número de WhatsApp personal al sandbox enviando el mensaje de activación (por ejemplo, `join company-slug`) desde tu WhatsApp al número del sandbox.

### Paso 6: Guarda y reinicia la aplicación

Una vez que hayas guardado el archivo con tus secretos, reinicia la aplicación para que se apliquen los cambios.

```bash
docker-compose up --build
```

El archivo `.gitignore` del proyecto ya está configurado para **ignorar** el archivo `secrets.toml`, por lo que tus credenciales permanecerán seguras en tu máquina local y no se subirán al repositorio.

---

## ▶️ Ejecución con Docker (Recomendado)

La forma más sencilla de ejecutar todo el sistema, incluido el chat con Llama 3.

### Prerrequisitos

*   **Docker y Docker Compose**: La forma más fácil es usar [Docker Desktop](https://www.docker.com/products/docker-desktop/).
*   **Git**: Para clonar el repositorio.

### Pasos

1.  **Clona el repositorio** (si no lo has hecho ya):
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

# streamlit_app.py

import streamlit as st
from twilio.rest import Client
from ollama_manager import OllamaManager # Importar el nuevo manager

# --- Configuración de la Página ---
st.set_page_config(page_title="Configurador y Verificador", layout="centered")

st.title("⚙️ Configurador de Usuario y Verificador de WhatsApp")
st.write("Introduce tus datos para configurar tu perfil y enviar un mensaje de prueba a través de WhatsApp.")

# --- Formulario de Configuración ---
with st.form("user_config_form"):
    st.header("Datos del Usuario")
    name = st.text_input("Nombre Completo")
    email = st.text_input("Correo Electrónico")
    password = st.text_input("Contraseña", type="password", help="Introduce una contraseña para el servicio externo.")
    whatsapp_number = st.text_input("Número de WhatsApp", placeholder="Ej: +5211234567890", help="Incluye el código de país y el '1' si es necesario.")

    st.header("Verificación de Conexión")
    submitted = st.form_submit_button("Guardar y Enviar Mensaje de Prueba")

# --- Lógica de Verificación ---
if submitted:
    # Validar que los campos no estén vacíos
    if not all([name, email, password, whatsapp_number]):
        st.warning("Por favor, rellena todos los campos antes de continuar.")
    else:
        try:
            # Cargar secretos de Twilio desde el archivo secrets.toml
            account_sid = st.secrets["TWILIO_ACCOUNT_SID"]
            auth_token = st.secrets["TWILIO_AUTH_TOKEN"]
            twilio_phone_number = st.secrets["TWILIO_PHONE_NUMBER"]

            # Validar que los secretos de Twilio están configurados
            if not all([account_sid, auth_token, twilio_phone_number]):
                st.error("Error de configuración: Faltan las credenciales de Twilio en el archivo `.streamlit/secrets.toml`.")
                st.info("Por favor, asegúrate de que el administrador del sistema ha configurado las credenciales correctamente.")
            else:
                with st.spinner("Enviando mensaje de prueba a WhatsApp..."):
                    client = Client(account_sid, auth_token)

                    # --- CORRECCIÓN ---
                    # Asegurarse de que el número de origen (From) tenga el prefijo 'whatsapp:'
                    from_number = twilio_phone_number
                    if not from_number.startswith('whatsapp:'):
                        from_number = f'whatsapp:{from_number}'

                    # Construcción del mensaje
                    message_body = f"¡Hola {name}! 👋 Tu conexión está funcionando correctamente. Tus datos han sido registrados: Correo: {email}."
                    
                    # Envío del mensaje
                    message = client.messages.create(
                        from_=from_number, # Usar el número de origen corregido
                        body=message_body,
                        to=f'whatsapp:{whatsapp_number}'
                    )

                    st.success("¡Mensaje enviado con éxito! ✨")
                    st.info(f"El ID del mensaje (SID) es: {message.sid}")
                    st.balloons()

        except Exception as e:
            st.error(f"Ha ocurrido un error al intentar enviar el mensaje: {e}")
            st.warning("**Posibles causas:**\n" 
                       "- El número de WhatsApp no es válido o no está en el formato correcto (ej: `+521...`).\n" 
                       "- Las credenciales de Twilio (`secrets.toml`) son incorrectas.\n" 
                       "- Aún no has aceptado la conversación con el sandbox de Twilio en tu WhatsApp.")

# --- Separador ---
st.divider()

# --- Interfaz de Chat con Llama 3 ---
st.title("💬 Chat con Llama 3")
st.write("Haz una pregunta o pídele algo a Llama 3.")

# Inicializar el manager de Ollama
try:
    ollama_manager = OllamaManager()
except Exception as e:
    st.error(f"No se pudo inicializar OllamaManager: {e}")
    st.stop()


# Inicializar el historial de chat en st.session_state
if "messages" not in st.session_state:
    st.session_state.messages = []

# Mostrar mensajes previos
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Aceptar entrada del usuario
if prompt := st.chat_input("¿Qué quieres saber?"):
    # Añadir mensaje del usuario al historial
    st.session_state.messages.append({"role": "user", "content": prompt})
    # Mostrar mensaje del usuario
    with st.chat_message("user"):
        st.markdown(prompt)

    # Obtener y mostrar respuesta del modelo
    with st.chat_message("assistant"):
        with st.spinner("Llama 3 está pensando..."):
            response = ollama_manager.get_ollama_response(model="llama3", prompt=prompt)
            st.markdown(response)
    
    # Añadir respuesta del modelo al historial
    st.session_state.messages.append({"role": "assistant", "content": response})

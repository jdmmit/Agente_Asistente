# streamlit_app.py

import streamlit as st
import requests
import time
import os

# --- Configuración de la Conexión con el Agente ---

# Detecta si estamos en un contenedor de Docker y ajusta la URL de la API en consecuencia.
if os.getenv('RUNNING_IN_DOCKER') == 'true':
    # Dentro de Docker, 'agent' es el nombre del servicio que Docker resuelve a la IP correcta.
    AGENT_API_URL = "http://agent:5000/api/command"
else:
    # Fuera de Docker, la API se ejecuta en el localhost.
    AGENT_API_URL = "http://localhost:5000/api/command"

st.title("Memorae - Your Local AI Assistant")

# --- Funciones de Comunicación con la API ---

def get_agent_response(prompt: str) -> str:
    """
    Envía un prompt al servicio del agente y obtiene una respuesta.
    """
    try:
        st.write(f"Connecting to agent at: {AGENT_API_URL}") # Línea de depuración
        response = requests.post(AGENT_API_URL, json={"prompt": prompt})
        response.raise_for_status()
        data = response.json()
        return data.get("response", "Error: La respuesta de la API no tiene el formato esperado.")

    except requests.exceptions.RequestException as e:
        st.error(f"Error de conexión con el agente: {e}")
        return "Lo siento, no puedo comunicarme con mi cerebro en este momento. Asegúrate de que el servicio del agente se esté ejecutando."

# --- Lógica de la Interfaz de Chat ---

if 'messages' not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("What is up?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        assistant_response = get_agent_response(prompt)
        full_response = ""
        for chunk in assistant_response.split():
            full_response += chunk + " "
            time.sleep(0.05)
            message_placeholder.markdown(full_response + "▌")
        message_placeholder.markdown(full_response)

    st.session_state.messages.append({"role": "assistant", "content": full_response})

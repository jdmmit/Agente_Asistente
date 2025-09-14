# streamlit_app.py

import streamlit as st
from agent_core import JDMMitAgente

st.title("Memorae - Your Local AI Assistant")

if 'agent' not in st.session_state:
    st.session_state.agent = JDMMitAgente()
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
        full_response = ""
        # This is a placeholder for the agent's response
        # We will replace this with a call to the agent's logic
        assistant_response = st.session_state.agent.run_single_command(prompt) 
        # Simulate stream of response with milliseconds delay
        for chunk in assistant_response.split():
            full_response += chunk + " "
            time.sleep(0.05)
            # Add a blinking cursor to simulate typing
            message_placeholder.markdown(full_response + "▌")
        message_placeholder.markdown(full_response)
    st.session_state.messages.append({"role": "assistant", "content": full_response})

# Agente Asistente "Memorae" - Local con Python y Ollama

## Introducción

Memorae es un asistente AI local similar a un chatbot personal con memoria, diseñado para ayudarte en tu día a día. Corre completamente en tu PC (Windows), sin necesidad de internet después de la instalación inicial, priorizando privacidad y eficiencia. Usa Ollama para un LLM local (como Llama3) que procesa consultas en español natural.

**Funciones clave**:

- **Manejo de tareas y recordatorios**: Crea, lista y completa tareas con fechas/prioridades. Guarda en base de datos local (SQLite).
- **Memoria persistente**: Recuerda conversaciones y contexto histórico para respuestas contextuales.
- **Integraciones**:
  - Google Calendar: Agrega eventos automáticamente.
  - Email: Envía recordatorios via SMTP (e.g., Gmail).
  - WhatsApp: Envía mensajes (usa pywhatkit; requiere WhatsApp Web abierto).
  - Notificaciones locales: Pop-ups en tu escritorio.
- **Respuestas diarias y resúmenes**: Responde preguntas generales y resume notas.
- **Modo voz**: Opcional; escucha y habla en español usando micrófono/altavoces.
- **Escalabilidad**: Fácil agregar voz avanzada, UI web (Streamlit), multi-usuario o más integraciones.

Es modular y extensible: El código usa clases para memoria e integraciones, permitiendo expansiones como Docker o APIs adicionales.

## Requisitos

- **Sistema**: Windows 11 (tu OS), Python 3.8+.
- **Hardware**: Mínimo 8GB RAM (para modelo LLM); GPU recomendada para velocidad (Ollama soporta NVIDIA).
- **Herramientas**:
  - Ollama (para LLM local).
  - Dependencias Python: Ver `requirements.txt`.
- **Cuentas externas** (opcional para integraciones):
  - Google Account para Calendar API.
  - Gmail para email (con app password).
  - WhatsApp Web para mensajes.

## Instalación Paso a Paso

1. **Clona o navega al proyecto**:

   - El proyecto está en `c:/Users/CTRL/Desktop/Convertir Pdf a Word/agente_asistente/`.
   - Abre CMD/Terminal en este directorio.

2. **Instala Ollama**:

   - Descarga el instalador desde [ollama.com/download](https://ollama.com/download) (elige Windows).
   - Instala y verifica: `ollama --version`.
   - Descarga el modelo LLM (con internet): `ollama pull llama3` (~4.7GB; solo una vez). Para más ligero: `ollama pull phi3`.

3. **Configura Entorno Python**:

   - Crea entorno virtual: `python -m venv venv`.
   - Activa: `venv\Scripts\activate` (en CMD).
   - Instala dependencias: `pip install -r requirements.txt`.
     - Nota: Si errores, ejecuta `pip install --upgrade pip` primero.
     - Para voz: Asegura micrófono/altavoces configurados.

4. **Configura Integraciones**:
   - **Google Calendar**:
     - Ve a [console.cloud.google.com](https://console.cloud.google.com).
     - Crea un proyecto nuevo, habilita "Google Calendar API".
     - Crea credenciales OAuth 2.0 (Client ID para app de escritorio), descarga `credentials.json` y colócalo en `agente_asistente/`.
     - Primera ejecución: Autoriza en browser (crea `token.pickle` automáticamente).
   - **Email**:
     - Edita `agente.py` (líneas ~20-22): Cambia `EMAIL_USER` por tu email y `EMAIL_PASS` por app password de Gmail.
     - Configura app password: En [myaccount.google.com/apppasswords](https://myaccount.google.com/apppasswords) (activa 2FA primero).
   - **WhatsApp**:
     - Edita `enviar_whatsapp()` en `agente.py`: Cambia `+573xxxxxxxxx` por tu número (formato internacional).
     - Abre WhatsApp Web en tu browser y escanea QR (pywhatkit lo usa).
   - **Notificaciones locales**: Funciona out-of-the-box con plyer.
   - **Base de datos**: Se crea automáticamente (`memoria.db`).

## Cómo Ejecutar

1. En CMD (con venv activado, en `agente_asistente/`): `python agente.py`.
2. **Modo CLI** (predeterminado):
   - Ingresa consultas: e.g., "Recuérdame la reunión mañana a las 10am con alta prioridad".
   - El agente responde, guarda en DB, y ejecuta acciones (notif/email/etc.).
   - Comandos especiales:
     - "Lista mis tareas" → Muestra pendientes.
     - "Completa la tarea 1" → Marca como hecha (ID de lista).
     - "Resumir notas de ayer" → LLM genera resumen (expande DB para notas full).
   - Salir: Escribe "salir".
3. **Modo Voz**:
   - Al inicio, responde "s" a "¿Usar modo voz?".
   - Habla consultas; responde en voz. Di "salir" para terminar.
   - Nota: Usa Google Speech-to-Text (requiere internet inicial; considera Whisper offline para full local).

**Ejemplo de Uso**:

- Input: "Agrega tarea: comprar leche el 2025-09-15 a las 09:00, envía email."
- Output: "Tarea guardada. Email enviado." (integra Calendar si configuras).
- Memoria: En consultas futuras, recuerda: "Basado en tu tarea de leche..."

Para UI web (escalabilidad): Instala Streamlit, modifica `main()` con `st.chat_input()`, corre `streamlit run agente.py` (abre localhost:8501).

## Cómo Funciona (Arquitectura Interna)

El agente sigue un flujo simple y modular:

1. **Input**: Usuario via CLI o voz.
2. **Memoria**: Recupera historial reciente de SQLite (contexto para LLM).
3. **Procesamiento LLM**: Ollama (`llama3`) genera respuesta con prompt contextual. Parsea como JSON para acciones (tarea/listar/etc.).
4. **Acciones**:
   - Guarda/lista tareas en DB.
   - Integra: Llama APIs (Calendar/email/WhatsApp) o notifica local.
5. **Output**: Respuesta textual/voz, guarda interacción en DB.
6. **Persistencia**: Todo en `memoria.db` (tablas: `historial`, `tareas`).

**Diagrama de Flujo** (Mermaid):

```mermaid
graph TD
    A[Usuario ingresa consulta via CLI/Voz] --> B[Recuperar memoria de SQLite<br/>(historial, tareas pendientes)]
    B --> C[Ollama procesa con contexto<br/>(parsear intent: tarea/recordatorio/respuesta)]
    C --> D{¿Integración externa?}
    D -->|Sí e.g. Calendar/Email| E[Llamar API: agregar evento/enviar notif]
    D -->|No| F[Generar respuesta con LLM]
    E --> F
    F --> G[Guardar actualización en SQLite<br/>(nueva tarea/resumen)]
    G --> H[Output al usuario<br/>(texto/voz/notif)]
    H --> I[Fin de interacción<br/>(loop para próxima)]
```

- **Privacidad**: No envía datos a servidores; LLM local.
- **Eficiencia**: Ollama optimiza; usa modelos pequeños para PCs modestas.

## Escalabilidad y Mejoras

- **Agregar Voz Avanzada**: Reemplaza speech_recognition por Whisper (local) en `escuchar_voz()`.
- **UI Web**: Integra Streamlit para chat graphical: Agrega `import streamlit as st` y loop con `st.chat_message`.
- **Multi-Usuario**: Agrega campo `user_id` en DB; autentica con input.
- **Más Integraciones**: Agrega clases en `Integrations` para Todoist/Notion via APIs.
- **Despliegue**: Crea `Dockerfile` para contenedor (instala Ollama en Docker).
- **Rendimiento**: Monitorea con `logging`; migra DB a PostgreSQL para grandes volúmenes.
- **Mantenimiento**: Actualiza Ollama: `ollama pull llama3` periódicamente. Para resúmenes avanzados, agrega tabla `notas` en DB.

## Troubleshooting

- **Ollama no responde**: Verifica `ollama list`; reinicia servicio.
- **Error en voz**: Instala `pip install pyaudio` (para micrófono en Windows).
- **Google API falla**: Revisa `credentials.json`; borra `token.pickle` y re-autoriza.
- **Email no envía**: Verifica app password y puerto (587 para TLS).
- **WhatsApp error**: Asegura browser abierto en WhatsApp Web.
- **Lento**: Cambia `MODEL = 'phi3'` o usa GPU (instala CUDA si NVIDIA).
- **Dependencias rotas**: `pip uninstall <paquete>` y reinstala.

Si necesitas expansiones, edita `agente.py` (modular). ¡Disfruta tu asistente diario!

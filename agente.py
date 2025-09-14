import sqlite3
import json
import datetime
import smtplib
from email.mime.text import MIMEText
import pywhatkit as pwk
from plyer import notification
import ollama
import speech_recognition as sr
import pyttsx3
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import pickle
import os
from google.auth.transport.requests import Request
import os.path

# Configuraciones (ajusta según tu setup)
MODEL = 'llama3'
DB_PATH = 'memoria.db'
CREDENTIALS_PATH = 'credentials.json'  # Para Google Calendar
EMAIL_SMTP = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USER = 'tu_email@gmail.com'  # Cambia por el tuyo
EMAIL_PASS = 'tu_app_password'  # App password de Gmail

class MemoryManager:
    def __init__(self, db_path):
        self.db_path = db_path
        self.init_db()

    def init_db(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        # Tabla para historial de conversaciones
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS historial (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                usuario_input TEXT,
                agente_output TEXT
            )
        ''')
        # Tabla para tareas y recordatorios
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tareas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                descripcion TEXT,
                fecha TEXT,
                prioridad TEXT,
                completada BOOLEAN DEFAULT FALSE,
                timestamp TEXT
            )
        ''')
        conn.commit()
        conn.close()

    def guardar_interaccion(self, input_usuario, output_agente):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        timestamp = datetime.datetime.now().isoformat()
        cursor.execute('INSERT INTO historial (timestamp, usuario_input, agente_output) VALUES (?, ?, ?)',
                       (timestamp, input_usuario, output_agente))
        conn.commit()
        conn.close()

    def guardar_tarea(self, descripcion, fecha=None, prioridad='media'):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        timestamp = datetime.datetime.now().isoformat()
        fecha = fecha or timestamp
        cursor.execute('INSERT INTO tareas (descripcion, fecha, prioridad, timestamp) VALUES (?, ?, ?, ?)',
                       (descripcion, fecha, prioridad, timestamp))
        conn.commit()
        conn.close()

    def listar_tareas(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM tareas WHERE completada = FALSE ORDER BY fecha')
        tareas = cursor.fetchall()
        conn.close()
        return tareas

    def obtener_historial_reciente(self, limit=5):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT usuario_input, agente_output FROM historial ORDER BY id DESC LIMIT ?', (limit,))
        historial = cursor.fetchall()
        conn.close()
        return historial[::-1]  # Revertir para orden cronológico

    def marcar_tarea_completada(self, tarea_id):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('UPDATE tareas SET completada = TRUE WHERE id = ?', (tarea_id,))
        conn.commit()
        conn.close()

def configurar_voz():
    engine = pyttsx3.init()
    recognizer = sr.Recognizer()
    return engine, recognizer

def escuchar_voz(recognizer):
    with sr.Microphone() as source:
        print("Escuchando...")
        audio = recognizer.listen(source)
    try:
        return recognizer.recognize_google(audio, language='es-ES')
    except:
        return None

def hablar_voz(engine, texto):
    engine.say(texto)
    engine.runAndWait()

def integrar_calendar(descripcion, fecha):
    # Placeholder para Google Calendar
    if os.path.exists(CREDENTIALS_PATH):
        SCOPES = ['https://www.googleapis.com/auth/calendar']
        creds = None
        if os.path.exists('token.pickle'):
            with open('token.pickle', 'rb') as token:
                creds = pickle.load(token)
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_PATH, SCOPES)
                creds = flow.run_local_server(port=0)
            with open('token.pickle', 'wb') as token:
                pickle.dump(creds, token)
        service = build('calendar', 'v3', credentials=creds)
        event = {
            'summary': descripcion,
            'start': {'dateTime': fecha},
            'end': {'dateTime': fecha},  # Ajusta duración
        }
        service.events().insert(calendarId='primary', body=event).execute()
        return "Evento agregado a Google Calendar."
    else:
        return "Configura credentials.json para Google Calendar."

def enviar_email(destinatario, asunto, cuerpo):
    msg = MIMEText(cuerpo)
    msg['Subject'] = asunto
    msg['From'] = EMAIL_USER
    msg['To'] = destinatario
    try:
        server = smtplib.SMTP(EMAIL_SMTP, EMAIL_PORT)
        server.starttls()
        server.login(EMAIL_USER, EMAIL_PASS)
        server.sendmail(EMAIL_USER, destinatario, msg.as_string())
        server.quit()
        return "Email enviado."
    except Exception as e:
        return f"Error enviando email: {e}"

def enviar_whatsapp(numero, mensaje):
    try:
        pwk.sendwhatmsg_instantly(numero, mensaje)
        return "Mensaje WhatsApp enviado."
    except Exception as e:
        return f"Error en WhatsApp: {e}. Asegúrate de que WhatsApp Web esté abierto."

def notificacion_local(titulo, mensaje):
    notification.notify(title=titulo, message=mensaje, timeout=10)

def chat_with_ollama(input_usuario, historial_reciente):
    contexto = "\n".join([f"Usuario: {h[0]}\nAsistente: {h[1]}" for h in historial_reciente])
    prompt = f"""Eres un asistente diario con memoria llamado Memorae. Ayuda con tareas, recordatorios, resúmenes y preguntas diarias.
Usa español natural. Contexto de memoria:
{contexto}

Consulta actual: {input_usuario}

Responde de forma útil. Si es una tarea o recordatorio, responde con JSON: {{"tipo": "tarea", "descripcion": "...", "fecha": "YYYY-MM-DDTHH:MM", "prioridad": "baja/media/alta", "accion": "guardar/email/calendar/whatsapp/notif"}}.
Si es listar tareas, responde: {{"tipo": "listar"}}.
Si es completar tarea, {{"tipo": "completar", "id": 1}}.
Para resumen de notas, {{"tipo": "resumen", "notas": "texto"}}.
Para respuesta simple, solo texto natural."""
    
    response = ollama.chat(model=MODEL, messages=[{'role': 'user', 'content': prompt}])
    return response['message']['content']

def procesar_respuesta(respuesta):
    try:
        # Intentar parsear JSON si parece uno
        if respuesta.startswith('{'):
            return json.loads(respuesta)
        else:
            return {'tipo': 'respuesta', 'contenido': respuesta}
    except:
        return {'tipo': 'respuesta', 'contenido': respuesta}

def main():
    memory = MemoryManager(DB_PATH)
    use_voice = input("¿Usar modo voz? (s/n): ").lower() == 's'
    
    if use_voice:
        engine, recognizer = configurar_voz()
        print("Modo voz activado. Di 'salir' para terminar.")
    
    while True:
        if use_voice:
            input_usuario = escuchar_voz(recognizer)
            if input_usuario and 'salir' in input_usuario.lower():
                break
            if not input_usuario:
                continue
            print(f"Tú: {input_usuario}")
        else:
            input_usuario = input("Tú: ")
            if input_usuario.lower() == 'salir':
                break
        
        historial_reciente = memory.obtener_historial_reciente()
        respuesta_llm = chat_with_ollama(input_usuario, historial_reciente)
        parsed = procesar_respuesta(respuesta_llm)
        
        if parsed['tipo'] == 'tarea':
            memory.guardar_tarea(parsed['descripcion'], parsed.get('fecha'), parsed['prioridad'])
            accion = parsed.get('accion', 'notif')
            if accion == 'email':
                enviar_email('destinatario@example.com', 'Recordatorio', parsed['descripcion'])  # Ajusta
            elif accion == 'calendar':
                integrar_calendar(parsed['descripcion'], parsed['fecha'])
            elif accion == 'whatsapp':
                enviar_whatsapp('+573xxxxxxxxx', parsed['descripcion'])  # Ajusta número
            else:
                notificacion_local('Nueva Tarea', parsed['descripcion'])
            output = f"Tarea guardada: {parsed['descripcion']}. Acción: {accion}."
        elif parsed['tipo'] == 'listar':
            tareas = memory.listar_tareas()
            output = "Tareas pendientes:\n" + "\n".join([f"{t[0]}: {t[1]} ({t[2]})" for t in tareas])
        elif parsed['tipo'] == 'completar':
            memory.marcar_tarea_completada(parsed['id'])
            output = "Tarea completada."
        elif parsed['tipo'] == 'resumen':
            # Placeholder para resumir notas (puedes agregar tabla de notas)
            output = "Resumen: " + parsed['notas']  # LLM ya resumió
        else:
            output = parsed['contenido']
        
        if use_voice:
            hablar_voz(engine, output)
        print(f"Memorae: {output}")
        
        memory.guardar_interaccion(input_usuario, output)

if __name__ == "__main__":
    main()
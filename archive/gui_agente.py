import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading
import queue
import mysql.connector
import datetime
import json
from config import MODEL, DB_CONFIG, ASSISTANT_NAME
import ollama
import logging
import os
from tkinter import font as tkfont

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AgenteGUI:
    def __init__(self, root):
        self.root = root
        self.root.title(f"{ASSISTANT_NAME} - Asistente AI Local")
        self.root.geometry("1000x700")
        self.root.configure(bg='#2b2b2b')
        
        # Cola para comunicación entre hilos
        self.message_queue = queue.Queue()
        
        # Variables de estado
        self.is_processing = False
        self.voice_enabled = tk.BooleanVar(value=False)
        self.auto_scroll = tk.BooleanVar(value=True)
        
        # Inicializar base de datos
        self.init_db()
        
        # Crear la interfaz
        self.create_widgets()
        
        # Configurar estilos
        self.configure_styles()
        
        # Cargar historial
        self.load_chat_history()
        
        # Iniciar procesamiento de mensajes
        self.root.after(100, self.process_queue)
        
    def configure_styles(self):
        """Configurar estilos personalizados"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configurar colores para tema oscuro
        style.configure('TFrame', background='#2b2b2b')
        style.configure('TLabel', background='#2b2b2b', foreground='white')
        style.configure('TButton', background='#404040', foreground='white')
        style.map('TButton', background=[('active', '#555555')])
        
    def init_db(self):
        """Inicializar base de datos MySQL"""
        try:
            conn = mysql.connector.connect(**DB_CONFIG)
            cursor = conn.cursor()
            
            # Tabla para historial
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS historial (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    usuario_input TEXT NOT NULL,
                    agente_output TEXT NOT NULL,
                    INDEX idx_historial_timestamp (timestamp)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
            ''')
            
            # Tabla para tareas
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS tareas (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    descripcion TEXT NOT NULL,
                    fecha DATETIME NULL,
                    prioridad ENUM('baja','media','alta') DEFAULT 'media',
                    completada BOOLEAN DEFAULT FALSE,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    categoria VARCHAR(64) DEFAULT 'general',
                    notas TEXT,
                    INDEX idx_tareas_completada (completada),
                    INDEX idx_tareas_prioridad (prioridad)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
            ''')
            
            conn.commit()
            conn.close()
            logger.info("Base de datos MySQL inicializada correctamente")
        except Exception as e:
            logger.error(f"Error inicializando base de datos: {e}")
            messagebox.showerror("Error de Base de Datos", f"No se pudo conectar a MySQL: {e}")
        
    def create_widgets(self):
        """Crear la interfaz de usuario"""
        # Frame principal
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Título
        title_label = tk.Label(main_frame, text=f"🤖 {ASSISTANT_NAME} - Asistente AI", 
                              font=('Arial', 16, 'bold'), 
                              bg='#2b2b2b', fg='#4a9eff')
        title_label.pack(pady=(0, 10))
        
        # Notebook para pestañas
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Pestaña de Chat
        self.create_chat_tab()
        
        # Pestaña de Tareas
        self.create_tasks_tab()
        
        # Pestaña de Configuración
        self.create_config_tab()
        
    def create_chat_tab(self):
        """Crear pestaña de chat"""
        chat_frame = ttk.Frame(self.notebook)
        self.notebook.add(chat_frame, text="💬 Chat")
        
        # Frame para el área de chat
        chat_area_frame = ttk.Frame(chat_frame)
        chat_area_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Área de conversación
        self.chat_display = scrolledtext.ScrolledText(
            chat_area_frame, 
            wrap=tk.WORD, 
            width=80, 
            height=25,
            bg='#1e1e1e',
            fg='white',
            insertbackground='white',
            font=('Consolas', 10)
        )
        self.chat_display.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Frame para entrada
        input_frame = ttk.Frame(chat_frame)
        input_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Campo de entrada
        self.entry_var = tk.StringVar()
        self.message_entry = tk.Entry(
            input_frame, 
            textvariable=self.entry_var,
            font=('Arial', 11),
            bg='#404040',
            fg='white',
            insertbackground='white'
        )
        self.message_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        self.message_entry.bind('<Return>', self.send_message)
        
        # Botón enviar
        self.send_button = tk.Button(
            input_frame, 
            text="Enviar",
            command=self.send_message,
            bg='#4a9eff',
            fg='white',
            font=('Arial', 10, 'bold'),
            relief=tk.FLAT,
            padx=20
        )
        self.send_button.pack(side=tk.RIGHT)
        
        # Frame para controles
        controls_frame = ttk.Frame(chat_frame)
        controls_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Checkbox para voz
        voice_check = tk.Checkbutton(
            controls_frame,
            text="🎤 Modo Voz",
            variable=self.voice_enabled,
            bg='#2b2b2b',
            fg='white',
            selectcolor='#404040',
            activebackground='#2b2b2b',
            activeforeground='white'
        )
        voice_check.pack(side=tk.LEFT)
        
        # Checkbox para auto-scroll
        scroll_check = tk.Checkbutton(
            controls_frame,
            text="📜 Auto-scroll",
            variable=self.auto_scroll,
            bg='#2b2b2b',
            fg='white',
            selectcolor='#404040',
            activebackground='#2b2b2b',
            activeforeground='white'
        )
        scroll_check.pack(side=tk.LEFT, padx=(20, 0))
        
        # Botón limpiar chat
        clear_button = tk.Button(
            controls_frame,
            text="🗑️ Limpiar Chat",
            command=self.clear_chat,
            bg='#d9534f',
            fg='white',
            relief=tk.FLAT,
            padx=10
        )
        clear_button.pack(side=tk.RIGHT)
        
    def create_tasks_tab(self):
        """Crear pestaña de tareas"""
        tasks_frame = ttk.Frame(self.notebook)
        self.notebook.add(tasks_frame, text="📋 Tareas")
        
        # Frame superior para nueva tarea
        new_task_frame = ttk.LabelFrame(tasks_frame, text="Nueva Tarea")
        new_task_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Entrada para nueva tarea
        self.task_entry = tk.Entry(
            new_task_frame,
            font=('Arial', 11),
            bg='#404040',
            fg='white',
            insertbackground='white'
        )
        self.task_entry.pack(fill=tk.X, padx=5, pady=5)
        self.task_entry.bind('<Return>', self.add_task)
        
        # Frame para prioridad y fecha
        task_options_frame = ttk.Frame(new_task_frame)
        task_options_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Prioridad
        ttk.Label(task_options_frame, text="Prioridad:").pack(side=tk.LEFT)
        self.priority_var = tk.StringVar(value="media")
        priority_combo = ttk.Combobox(
            task_options_frame,
            textvariable=self.priority_var,
            values=["baja", "media", "alta"],
            width=10
        )
        priority_combo.pack(side=tk.LEFT, padx=5)
        
        # Botón agregar tarea
        add_task_btn = tk.Button(
            task_options_frame,
            text="➕ Agregar",
            command=self.add_task,
            bg='#5cb85c',
            fg='white',
            relief=tk.FLAT
        )
        add_task_btn.pack(side=tk.RIGHT)
        
        # Lista de tareas
        tasks_list_frame = ttk.LabelFrame(tasks_frame, text="Tareas Pendientes")
        tasks_list_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Treeview para mostrar tareas
        columns = ('ID', 'Descripción', 'Prioridad', 'Fecha')
        self.tasks_tree = ttk.Treeview(tasks_list_frame, columns=columns, show='headings', height=10)
        
        # Configurar columnas
        self.tasks_tree.heading('ID', text='ID')
        self.tasks_tree.heading('Descripción', text='Descripción')
        self.tasks_tree.heading('Prioridad', text='Prioridad')
        self.tasks_tree.heading('Fecha', text='Fecha')
        
        self.tasks_tree.column('ID', width=50)
        self.tasks_tree.column('Descripción', width=300)
        self.tasks_tree.column('Prioridad', width=80)
        self.tasks_tree.column('Fecha', width=120)
        
        # Scrollbar para la lista
        tasks_scrollbar = ttk.Scrollbar(tasks_list_frame, orient=tk.VERTICAL, command=self.tasks_tree.yview)
        self.tasks_tree.configure(yscrollcommand=tasks_scrollbar.set)
        
        self.tasks_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        tasks_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Frame para botones de tareas
        tasks_buttons_frame = ttk.Frame(tasks_frame)
        tasks_buttons_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Botones de gestión de tareas
        complete_btn = tk.Button(
            tasks_buttons_frame,
            text="✅ Completar",
            command=self.complete_task,
            bg='#5cb85c',
            fg='white',
            relief=tk.FLAT
        )
        complete_btn.pack(side=tk.LEFT, padx=5)
        
        delete_btn = tk.Button(
            tasks_buttons_frame,
            text="🗑️ Eliminar",
            command=self.delete_task,
            bg='#d9534f',
            fg='white',
            relief=tk.FLAT
        )
        delete_btn.pack(side=tk.LEFT, padx=5)
        
        refresh_btn = tk.Button(
            tasks_buttons_frame,
            text="🔄 Actualizar",
            command=self.refresh_tasks,
            bg='#f0ad4e',
            fg='white',
            relief=tk.FLAT
        )
        refresh_btn.pack(side=tk.RIGHT, padx=5)
        
        # Cargar tareas
        self.refresh_tasks()
        
    def create_config_tab(self):
        """Crear pestaña de configuración"""
        config_frame = ttk.Frame(self.notebook)
        self.notebook.add(config_frame, text="⚙️ Configuración")
        
        # Frame para configuraciones
        settings_frame = ttk.LabelFrame(config_frame, text=f"Configuraciones de {ASSISTANT_NAME}")
        settings_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Modelo
        ttk.Label(settings_frame, text="Modelo LLM:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.model_var = tk.StringVar(value=MODEL)
        model_entry = tk.Entry(settings_frame, textvariable=self.model_var, width=30, bg='#404040', fg='white')
        model_entry.grid(row=0, column=1, padx=5, pady=5)
        
        # Frame para estadísticas
        stats_frame = ttk.LabelFrame(config_frame, text="Estadísticas")
        stats_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.stats_text = tk.Text(
            stats_frame,
            height=10,
            bg='#1e1e1e',
            fg='white',
            font=('Consolas', 10)
        )
        self.stats_text.pack(fill=tk.X, padx=5, pady=5)
        
        # Botón para actualizar estadísticas
        stats_btn = tk.Button(
            config_frame,
            text="📊 Actualizar Estadísticas",
            command=self.update_stats,
            bg='#5bc0de',
            fg='white',
            relief=tk.FLAT
        )
        stats_btn.pack(pady=10)
        
        # Cargar estadísticas iniciales
        self.update_stats()
        
    def send_message(self, event=None):
        """Enviar mensaje al agente"""
        if self.is_processing:
            messagebox.showwarning("Procesando", "El agente está procesando. Espera un momento.")
            return
            
        message = self.entry_var.get().strip()
        if not message:
            return
            
        # Limpiar entrada
        self.entry_var.set("")
        
        # Mostrar mensaje del usuario
        self.add_message_to_chat(f"👤 Tú: {message}", "user")
        
        # Procesar en hilo separado
        self.is_processing = True
        self.send_button.config(state=tk.DISABLED, text="Procesando...")
        
        thread = threading.Thread(target=self.process_message, args=(message,))
        thread.daemon = True
        thread.start()
        
    def process_message(self, message):
        """Procesar mensaje con el agente"""
        try:
            # Obtener historial reciente
            historial = self.get_recent_history()
            
            # Crear prompt
            contexto = "\n".join([f"Usuario: {h[0]}\nAsistente: {h[1]}" for h in historial])
            prompt = f"""Eres {ASSISTANT_NAME}, un asistente diario con memoria. Ayuda con tareas, recordatorios, resúmenes y preguntas diarias.
Usa español natural. Contexto de memoria:
{contexto}

Consulta actual: {message}

Responde de forma útil. Si es una tarea o recordatorio, responde con JSON: {{"tipo": "tarea", "descripcion": "...", "fecha": "YYYY-MM-DDTHH:MM", "prioridad": "baja/media/alta", "accion": "guardar/email/calendar/whatsapp/notif"}}.
Si es listar tareas, responde: {{"tipo": "listar"}}.
Si es completar tarea, {{"tipo": "completar", "id": 1}}.
Para respuesta simple, solo texto natural."""
            
            # Llamar a Ollama
            response = ollama.chat(model=MODEL, messages=[{'role': 'user', 'content': prompt}])
            agent_response = response['message']['content']
            
            # Procesar respuesta
            parsed = self.parse_response(agent_response)
            final_response = self.handle_parsed_response(parsed)
            
            # Guardar interacción
            self.save_interaction(message, final_response)
            
            # Enviar respuesta a la GUI
            self.message_queue.put(("response", final_response))
            
        except Exception as e:
            logger.error(f"Error procesando mensaje: {e}")
            self.message_queue.put(("error", f"Error: {str(e)}"))
        finally:
            self.message_queue.put(("done", None))
            
    def parse_response(self, response):
        """Parsear respuesta del agente"""
        try:
            if response.strip().startswith('{'):
                return json.loads(response)
            else:
                return {'tipo': 'respuesta', 'contenido': response}
        except:
            return {'tipo': 'respuesta', 'contenido': response}
            
    def handle_parsed_response(self, parsed):
        """Manejar respuesta parseada"""
        if parsed['tipo'] == 'tarea':
            # Guardar tarea en base de datos
            self.save_task(parsed['descripcion'], parsed.get('fecha'), parsed['prioridad'])
            return f"✅ Tarea guardada: {parsed['descripcion']} (Prioridad: {parsed['prioridad']})"
            
        elif parsed['tipo'] == 'listar':
            tasks = self.get_tasks()
            if tasks:
                task_list = "\n".join([f"• {t[1]} ({t[3]})" for t in tasks])
                return f"📋 Tareas pendientes:\n{task_list}"
            else:
                return "📋 No hay tareas pendientes."
                
        elif parsed['tipo'] == 'completar':
            task_id = parsed.get('id')
            if task_id:
                self.mark_task_completed(task_id)
                return f"✅ Tarea {task_id} marcada como completada."
            
        return parsed.get('contenido', str(parsed))
        
    def process_queue(self):
        """Procesar cola de mensajes"""
        try:
            while True:
                msg_type, content = self.message_queue.get_nowait()
                
                if msg_type == "response":
                    self.add_message_to_chat(f"🤖 {ASSISTANT_NAME}: {content}", "agent")
                elif msg_type == "error":
                    self.add_message_to_chat(f"❌ Error: {content}", "error")
                elif msg_type == "done":
                    self.is_processing = False
                    self.send_button.config(state=tk.NORMAL, text="Enviar")
                    
        except queue.Empty:
            pass
        finally:
            self.root.after(100, self.process_queue)
            
    def add_message_to_chat(self, message, msg_type="normal"):
        """Agregar mensaje al chat"""
        self.chat_display.config(state=tk.NORMAL)
        
        # Configurar colores según el tipo
        if msg_type == "user":
            self.chat_display.insert(tk.END, message + "\n\n", "user")
        elif msg_type == "agent":
            self.chat_display.insert(tk.END, message + "\n\n", "agent")
        elif msg_type == "error":
            self.chat_display.insert(tk.END, message + "\n\n", "error")
        else:
            self.chat_display.insert(tk.END, message + "\n\n")
            
        self.chat_display.config(state=tk.DISABLED)
        
        if self.auto_scroll.get():
            self.chat_display.see(tk.END)
            
        # Configurar tags de colores
        self.chat_display.tag_config("user", foreground="#4a9eff")
        self.chat_display.tag_config("agent", foreground="#5cb85c")
        self.chat_display.tag_config("error", foreground="#d9534f")
        
    def clear_chat(self):
        """Limpiar el chat"""
        if messagebox.askyesno("Confirmar", "¿Estás seguro de que quieres limpiar el chat?"):
            self.chat_display.config(state=tk.NORMAL)
            self.chat_display.delete(1.0, tk.END)
            self.chat_display.config(state=tk.DISABLED)
            
    # Métodos de base de datos MySQL
    def get_recent_history(self, limit=5):
        """Obtener historial reciente"""
        try:
            conn = mysql.connector.connect(**DB_CONFIG)
            cursor = conn.cursor()
            cursor.execute('SELECT usuario_input, agente_output FROM historial ORDER BY id DESC LIMIT %s', (limit,))
            history = cursor.fetchall()
            conn.close()
            return history[::-1]  # Revertir para orden cronológico
        except Exception as e:
            logger.error(f"Error obteniendo historial: {e}")
            return []
        
    def save_interaction(self, user_input, agent_output):
        """Guardar interacción en base de datos"""
        try:
            conn = mysql.connector.connect(**DB_CONFIG)
            cursor = conn.cursor()
            timestamp = datetime.datetime.now()
            cursor.execute('INSERT INTO historial (timestamp, usuario_input, agente_output) VALUES (%s, %s, %s)',
                          (timestamp, user_input, agent_output))
            conn.commit()
            conn.close()
        except Exception as e:
            logger.error(f"Error guardando interacción: {e}")
        
    def load_chat_history(self):
        """Cargar historial de chat"""
        history = self.get_recent_history(10)
        for user_msg, agent_msg in history:
            self.add_message_to_chat(f"👤 Tú: {user_msg}", "user")
            self.add_message_to_chat(f"🤖 {ASSISTANT_NAME}: {agent_msg}", "agent")
            
    # Métodos de tareas
    def add_task(self, event=None):
        """Agregar nueva tarea"""
        description = self.task_entry.get().strip()
        if not description:
            return
            
        priority = self.priority_var.get()
        self.save_task(description, None, priority)
        self.task_entry.delete(0, tk.END)
        self.refresh_tasks()
        messagebox.showinfo("Tarea Agregada", f"Tarea '{description}' agregada con prioridad {priority}")
        
    def save_task(self, description, fecha=None, priority='media'):
        """Guardar tarea en base de datos"""
        try:
            conn = mysql.connector.connect(**DB_CONFIG)
            cursor = conn.cursor()
            timestamp = datetime.datetime.now()
            fecha = fecha or timestamp
            cursor.execute('INSERT INTO tareas (descripcion, fecha, prioridad, timestamp) VALUES (%s, %s, %s, %s)',
                          (description, fecha, priority, timestamp))
            conn.commit()
            conn.close()
        except Exception as e:
            logger.error(f"Error guardando tarea: {e}")
        
    def get_tasks(self):
        """Obtener tareas pendientes"""
        try:
            conn = mysql.connector.connect(**DB_CONFIG)
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM tareas WHERE completada = FALSE ORDER BY fecha')
            tasks = cursor.fetchall()
            conn.close()
            return tasks
        except Exception as e:
            logger.error(f"Error obteniendo tareas: {e}")
            return []
        
    def refresh_tasks(self):
        """Actualizar lista de tareas"""
        # Limpiar lista actual
        for item in self.tasks_tree.get_children():
            self.tasks_tree.delete(item)
            
        # Cargar tareas
        tasks = self.get_tasks()
        for task in tasks:
            # Formatear fecha
            try:
                fecha = task[2].strftime("%Y-%m-%d %H:%M") if task[2] else "Sin fecha"
            except:
                fecha = str(task[2]) if task[2] else "Sin fecha"
                
            # Agregar al tree
            self.tasks_tree.insert('', tk.END, values=(task[0], task[1], task[3], fecha))
            
    def complete_task(self):
        """Marcar tarea como completada"""
        selected = self.tasks_tree.selection()
        if not selected:
            messagebox.showwarning("Selección", "Selecciona una tarea para completar.")
            return
            
        task_id = self.tasks_tree.item(selected[0])['values'][0]
        self.mark_task_completed(task_id)
        self.refresh_tasks()
        messagebox.showinfo("Tarea Completada", "La tarea ha sido marcada como completada.")
        
    def delete_task(self):
        """Eliminar tarea"""
        selected = self.tasks_tree.selection()
        if not selected:
            messagebox.showwarning("Selección", "Selecciona una tarea para eliminar.")
            return
            
        if messagebox.askyesno("Confirmar", "¿Estás seguro de que quieres eliminar esta tarea?"):
            task_id = self.tasks_tree.item(selected[0])['values'][0]
            try:
                conn = mysql.connector.connect(**DB_CONFIG)
                cursor = conn.cursor()
                cursor.execute('DELETE FROM tareas WHERE id = %s', (task_id,))
                conn.commit()
                conn.close()
                self.refresh_tasks()
            except Exception as e:
                logger.error(f"Error eliminando tarea: {e}")
            
    def mark_task_completed(self, task_id):
        """Marcar tarea como completada"""
        try:
            conn = mysql.connector.connect(**DB_CONFIG)
            cursor = conn.cursor()
            cursor.execute('UPDATE tareas SET completada = TRUE WHERE id = %s', (task_id,))
            conn.commit()
            conn.close()
        except Exception as e:
            logger.error(f"Error completando tarea: {e}")
        
    def update_stats(self):
        """Actualizar estadísticas"""
        try:
            conn = mysql.connector.connect(**DB_CONFIG)
            cursor = conn.cursor()
            
            # Estadísticas de conversaciones
            cursor.execute('SELECT COUNT(*) FROM historial')
            total_conversations = cursor.fetchone()[0]
            
            # Estadísticas de tareas
            cursor.execute('SELECT COUNT(*) FROM tareas WHERE completada = FALSE')
            pending_tasks = cursor.fetchone()[0]
            
            cursor.execute('SELECT COUNT(*) FROM tareas WHERE completada = TRUE')
            completed_tasks = cursor.fetchone()[0]
            
            # Últimas interacciones
            cursor.execute('SELECT timestamp FROM historial ORDER BY id DESC LIMIT 1')
            last_interaction = cursor.fetchone()
            last_interaction = str(last_interaction[0]) if last_interaction else "Nunca"
            
            conn.close()
            
            stats_text = f"""📊 ESTADÍSTICAS DE {ASSISTANT_NAME}

💬 Conversaciones totales: {total_conversations}
📋 Tareas pendientes: {pending_tasks}
✅ Tareas completadas: {completed_tasks}
🕐 Última interacción: {last_interaction}

🤖 Modelo actual: {MODEL}
💾 Base de datos: MySQL
📍 Host: {DB_CONFIG['host']}:{DB_CONFIG['port']}
🗄️  Database: {DB_CONFIG['database']}

🚀 Estado: Funcionando correctamente
"""
            
            self.stats_text.delete(1.0, tk.END)
            self.stats_text.insert(1.0, stats_text)
        except Exception as e:
            logger.error(f"Error actualizando estadísticas: {e}")
            self.stats_text.delete(1.0, tk.END)
            self.stats_text.insert(1.0, f"Error conectando a la base de datos: {e}")

def main():
    """Función principal"""
    root = tk.Tk()
    app = AgenteGUI(root)
    
    # Configurar cierre de aplicación
    def on_closing():
        if messagebox.askokcancel("Salir", "¿Estás seguro de que quieres salir?"):
            root.destroy()
    
    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()

if __name__ == "__main__":
    main()

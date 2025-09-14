
import pytest
import os
import sqlite3
from unittest.mock import patch, MagicMock

# Antes de importar el agente, configuramos las variables de entorno para una BD de prueba
# Así nos aseguramos de no tocar la base de datos de producción durante las pruebas
DB_TEST_FILE = "test_memorae.db"
os.environ['DATABASE_NAME'] = DB_TEST_FILE

# Importamos las clases necesarias después de configurar el entorno
from agent_core import JDMMitAgente
from database_manager import DatabaseManager

# --- Fixtures de Pytest --- #

@pytest.fixture(scope="module")
def test_db():
    """Fixture para crear y limpiar una base de datos de prueba para todos los tests."""
    # Limpieza antes de empezar: asegurarse de que no existe una BD de una ejecución anterior
    if os.path.exists(DB_TEST_FILE):
        os.remove(DB_TEST_FILE)
    
    # Se crea la instancia de la base de datos, lo que crea el archivo y las tablas
    db = DatabaseManager()
    db.close()
    
    # Cedemos el control a los tests
    yield DB_TEST_FILE
    
    # Limpieza después de que todos los tests del módulo hayan terminado
    if os.path.exists(DB_TEST_FILE):
        os.remove(DB_TEST_FILE)

@pytest.fixture
def mock_ollama():
    """Fixture para simular (mock) el OllamaManager y evitar llamadas reales a la red."""
    with patch('agent_core.OllamaManager') as mock:
        # Configuramos la instancia mock para que tenga un método 'chat'
        instance = mock.return_value
        # Por defecto, el mock de chat devolverá una respuesta de texto simple
        instance.chat.return_value = "{'tipo': 'respuesta', 'contenido': 'Hola de vuelta'}"
        yield instance

@pytest.fixture
def agente(test_db, mock_ollama):
    """Fixture para crear una instancia del agente con la BD de prueba y el Ollama simulado."""
    # Como ya hemos configurado la variable de entorno, el agente usará la BD de prueba
    # El patch del mock_ollama ya está activo aquí
    agente_instance = JDMMitAgente()
    yield agente_instance
    agente_instance.shutdown() # Asegurarse de que los recursos se liberan


# --- Pruebas del Agente --- #

def test_database_connection(test_db):
    """1. Prueba que la conexión a la base de datos se establece y las tablas se crean."""
    assert os.path.exists(test_db), "El archivo de la base de datos no fue creado."
    
    conn = sqlite3.connect(test_db)
    cursor = conn.cursor()
    
    # Verificar que las tablas principales existen
    tables = ['conversations', 'memories', 'tasks']
    for table in tables:
        cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table}';")
        assert cursor.fetchone() is not None, f"La tabla '{table}' no fue creada."
    
    conn.close()

def test_ollama_connection_mocked(agente, mock_ollama):
    """2. Prueba que el agente intenta comunicarse con Ollama (usando el mock)."""
    prompt = "hola"
    agente.execute_command(prompt)
    # Verificamos que el método 'chat' del mock de Ollama fue llamado una vez
    mock_ollama.chat.assert_called_once()

def test_simple_response(agente):
    """3. Prueba que un prompt simple recibe una respuesta con el formato esperado."""
    prompt = "hola"
    response = agente.execute_command(prompt)
    assert isinstance(response, str)
    assert response == "Hola de vuelta"

def test_create_memory_end_to_end(agente, mock_ollama, test_db):
    """4. Prueba de extremo a extremo: guardar una memoria y verificar en la BD."""
    # 1. Configurar el mock de Ollama para que devuelva una acción de memoria
    prompt_memoria = "Recuerda que mi color favorito es el azul"
    json_response = "{'tipo': 'memoria', 'categoria': 'preferencia_usuario', 'info': 'color favorito es azul'}"
    mock_ollama.chat.return_value = f"```json\n{json_response}\n```"

    # 2. Ejecutar el comando en el agente
    respuesta_agente = agente.execute_command(prompt_memoria)

    # 3. Verificar la respuesta del agente
    assert "He guardado la siguiente información" in respuesta_agente
    assert "preferencia_usuario" in respuesta_agente
    assert "color favorito es azul" in respuesta_agente

    # 4. Verificar directamente en la base de datos que la memoria fue guardada
    conn = sqlite3.connect(test_db)
    cursor = conn.cursor()
    cursor.execute("SELECT category, key, value FROM memories WHERE key = 'color favorito es azul'")
    memory_from_db = cursor.fetchone()
    conn.close()

    assert memory_from_db is not None, "La memoria no se encontró en la base de datos."
    assert memory_from_db[0] == "preferencia_usuario"
    assert memory_from_db[1] == "color favorito es azul"

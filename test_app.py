
import pytest
import os
import sqlite3  # Importación necesaria para la prueba de bajo nivel del esquema
from unittest.mock import patch

# Establecer la variable de entorno ANTES de que se importe cualquier módulo de la aplicación
DB_TEST_FILE = "test_memorae.db"
os.environ['DATABASE_NAME'] = DB_TEST_FILE

# Importar las clases necesarias DESPUÉS de configurar el entorno
from agent_core import JDMMitAgente
from database_manager import DatabaseManager

# --- Fixtures de Pytest --- #

@pytest.fixture(scope="module")
def db_setup_and_teardown():
    """(Módulo) Se asegura de que el archivo de la BD de pruebas esté limpio antes y después de las pruebas."""
    if os.path.exists(DB_TEST_FILE):
        os.remove(DB_TEST_FILE)
    
    yield
    
    if os.path.exists(DB_TEST_FILE):
        os.remove(DB_TEST_FILE)

@pytest.fixture
def mock_ollama():
    """Simula (mock) el OllamaManager para evitar llamadas reales a la red."""
    with patch('agent_core.OllamaManager') as mock:
        instance = mock.return_value
        instance.chat.return_value = '{"tipo": "respuesta", "contenido": "Hola de vuelta"}'
        yield instance

@pytest.fixture
def agente(db_setup_and_teardown, mock_ollama):
    """Crea una instancia del agente para cada prueba, asegurando un estado limpio."""
    agente_instance = JDMMitAgente()
    yield agente_instance
    agente_instance.shutdown()

# --- Pruebas del Agente --- #

def test_database_creation_and_schema(db_setup_and_teardown):
    """1. Prueba que DatabaseManager crea el archivo y el esquema de SQLite correctamente."""
    assert not os.path.exists(DB_TEST_FILE), "La base de datos no debería existir al empezar."
    
    db = DatabaseManager()
    
    assert os.path.exists(DB_TEST_FILE), "El archivo de la base de datos no fue creado."
    
    conn = sqlite3.connect(DB_TEST_FILE)
    cursor = conn.cursor()
    tables = ['conversations', 'memories', 'tasks']
    for table in tables:
        cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table}';")
        assert cursor.fetchone() is not None, f"La tabla '{table}' no fue creada en el esquema."
    conn.close()
    db.close()

def test_simple_response_from_mocked_ollama(agente):
    """2. Prueba que un prompt simple recibe la respuesta del mock de Ollama."""
    prompt = "hola"
    response = agente.execute_command(prompt)
    assert isinstance(response, str)
    assert response == "Hola de vuelta"

def test_end_to_end_create_and_verify_memory(agente, mock_ollama):
    """3. Prueba de extremo a extremo: guardar una memoria y verificarla usando el DatabaseManager."""
    prompt_memoria = "Recuerda que mi color favorito es el azul"
    json_string = '{"tipo": "memoria", "categoria": "preferencia_usuario", "info": "color favorito es azul"}'
    mock_ollama.chat.return_value = f"```json\n{json_string}\n```"

    respuesta_agente = agente.execute_command(prompt_memoria)

    assert "He guardado" in respuesta_agente
    assert "preferencia_usuario" in respuesta_agente
    assert "color favorito es azul" in respuesta_agente

    memory_from_db = agente.db.get_memory(key="color favorito es azul")

    assert memory_from_db is not None, "La memoria no se encontró en la base de datos."
    assert memory_from_db['category'] == "preferencia_usuario"
    assert memory_from_db['key'] == "color favorito es azul"

"""
Utilidades de Testing para BackendBot
Funciones comunes y fixtures para todos los tests
"""

import os
import sys
import tempfile
import shutil
import pytest
from pathlib import Path
from unittest.mock import Mock, MagicMock
import json
from datetime import datetime

# Configurar path del proyecto
project_root = Path(__file__).parent.parent
src_path = project_root / 'src'
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

class TestConfig:
    """Configuración para tests"""

    # Directorios de test
    TEST_DATA_DIR = project_root / 'tests' / 'fixtures'
    TEMP_DIR = Path(tempfile.gettempdir()) / 'backendbot_tests'

    # Configuración de base de datos de test
    TEST_DB_PATH = TEMP_DIR / 'test_backendbot.db'

    # Configuración de logging para tests
    LOG_LEVEL = 'WARNING'

    @classmethod
    def setup_class(cls):
        """Configuración inicial de la clase de test"""
        cls.TEMP_DIR.mkdir(exist_ok=True)

    @classmethod
    def teardown_class(cls):
        """Limpieza final de la clase de test"""
        if cls.TEMP_DIR.exists():
            shutil.rmtree(cls.TEMP_DIR)

def create_mock_file(path: Path, content: str = "", size_mb: int = 0) -> Path:
    """Crea un archivo mock para testing"""
    path.parent.mkdir(parents=True, exist_ok=True)

    if size_mb > 0:
        # Crear archivo de tamaño específico
        content = "x" * (size_mb * 1024 * 1024)

    path.write_text(content, encoding='utf-8')
    return path

def create_test_directory_structure(base_path: Path) -> dict:
    """Crea una estructura de directorios de prueba"""
    structure = {
        'documents': base_path / 'documents',
        'images': base_path / 'images',
        'videos': base_path / 'videos',
        'music': base_path / 'music',
        'downloads': base_path / 'downloads',
        'temp': base_path / 'temp'
    }

    for dir_path in structure.values():
        dir_path.mkdir(parents=True, exist_ok=True)

    # Crear algunos archivos de prueba
    test_files = [
        (structure['documents'] / 'document1.txt', 'Contenido del documento 1'),
        (structure['documents'] / 'document2.pdf', 'Contenido PDF'),
        (structure['images'] / 'image1.jpg', 'Datos de imagen JPG'),
        (structure['images'] / 'image2.png', 'Datos de imagen PNG'),
        (structure['videos'] / 'video1.mp4', 'Datos de video MP4'),
        (structure['music'] / 'song1.mp3', 'Datos de audio MP3'),
        (structure['downloads'] / 'download1.zip', 'Archivo ZIP'),
        (structure['temp'] / 'temp1.tmp', 'Archivo temporal'),
    ]

    for file_path, content in test_files:
        create_mock_file(file_path, content)

    return structure

def mock_system_info():
    """Retorna información mock del sistema"""
    return {
        'cpu_percent': 45.2,
        'memory_percent': 62.8,
        'disk_usage': {
            'total': 1000000000,  # 1GB
            'used': 600000000,    # 600MB
            'free': 400000000     # 400MB
        },
        'network_connections': 5,
        'running_processes': 85
    }

def mock_gpu_info():
    """Retorna información mock de GPU"""
    return {
        'gpu_count': 1,
        'gpu_0': {
            'name': 'NVIDIA GeForce RTX 3060',
            'memory_total': 12288,  # MB
            'memory_used': 4096,    # MB
            'memory_free': 8192,    # MB
            'temperature': 65,      # Celsius
            'utilization': 45       # %
        }
    }

def create_mock_database_data():
    """Crea datos mock para la base de datos"""
    return {
        'users': [
            {
                'id': 1,
                'username': 'test_user',
                'preferences': json.dumps({'theme': 'dark', 'language': 'es'}),
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat()
            }
        ],
        'tasks': [
            {
                'id': 1,
                'name': 'Test Task',
                'description': 'Tarea de prueba',
                'schedule': '0 */4 * * *',
                'enabled': True,
                'last_run': None,
                'next_run': datetime.now().isoformat(),
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat()
            }
        ],
        'metrics': [
            {
                'id': 1,
                'metric_type': 'cpu',
                'value': 45.2,
                'unit': '%',
                'timestamp': datetime.now().isoformat(),
                'metadata': json.dumps({'core': 'all'})
            }
        ]
    }

class MockDatabaseManager:
    """Mock del DatabaseManager para testing"""

    def __init__(self):
        self.connected = False
        self.data = create_mock_database_data()

    def connect(self):
        self.connected = True
        return Mock()

    def disconnect(self):
        self.connected = False

    def execute_query(self, query: str, params=None):
        """Simula ejecución de consultas SELECT"""
        if 'users' in query.lower():
            return self.data['users']
        elif 'tasks' in query.lower():
            return self.data['tasks']
        elif 'metrics' in query.lower():
            return self.data['metrics']
        return []

    def execute_update(self, query: str, params=None):
        """Simula ejecución de consultas INSERT/UPDATE/DELETE"""
        return 1

class TestDataFactory:
    """Fábrica para crear datos de prueba"""

    @staticmethod
    def create_user(username: str = "test_user", **kwargs):
        """Crea un usuario de prueba"""
        return {
            'id': 1,
            'username': username,
            'preferences': json.dumps(kwargs.get('preferences', {})),
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat()
        }

    @staticmethod
    def create_task(name: str = "Test Task", **kwargs):
        """Crea una tarea de prueba"""
        return {
            'id': 1,
            'name': name,
            'description': kwargs.get('description', 'Descripción de prueba'),
            'schedule': kwargs.get('schedule', '0 */4 * * *'),
            'enabled': kwargs.get('enabled', True),
            'last_run': kwargs.get('last_run'),
            'next_run': kwargs.get('next_run', datetime.now().isoformat()),
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat()
        }

    @staticmethod
    def create_metric(metric_type: str = "cpu", value: float = 50.0, **kwargs):
        """Crea una métrica de prueba"""
        return {
            'id': 1,
            'metric_type': metric_type,
            'value': value,
            'unit': kwargs.get('unit', '%'),
            'timestamp': datetime.now().isoformat(),
            'metadata': json.dumps(kwargs.get('metadata', {}))
        }

# Fixtures de pytest
@pytest.fixture(scope="session")
def test_config():
    """Fixture de configuración de test"""
    config = TestConfig()
    config.setup_class()
    yield config
    config.teardown_class()

@pytest.fixture
def temp_dir():
    """Fixture que proporciona un directorio temporal"""
    temp_path = Path(tempfile.mkdtemp())
    yield temp_path
    shutil.rmtree(temp_path)

@pytest.fixture
def mock_db():
    """Fixture que proporciona un mock de base de datos"""
    return MockDatabaseManager()

@pytest.fixture
def test_structure(temp_dir):
    """Fixture que crea una estructura de archivos de prueba"""
    return create_test_directory_structure(temp_dir / 'test_structure')

@pytest.fixture
def system_info():
    """Fixture con información mock del sistema"""
    return mock_system_info()

@pytest.fixture
def gpu_info():
    """Fixture con información mock de GPU"""
    return mock_gpu_info()
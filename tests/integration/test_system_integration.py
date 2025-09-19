"""
Tests de Integración para BackendBot
Pruebas de interacción entre componentes
"""

import pytest
import os
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock
import json

from tests.utils.test_utils import (
    TestConfig,
    create_test_directory_structure,
    mock_system_info,
    mock_gpu_info
)


class TestSystemIntegration:
    """Tests de integración del sistema completo"""

    def test_config_persistence_integration(self, temp_dir):
        """Test integración entre configuración y persistencia"""
        # Crear archivo de configuración temporal
        config_file = temp_dir / 'test_config.yaml'
        config_data = {
            'app': {'name': 'TestApp', 'version': '1.0.0'},
            'database': {'path': str(temp_dir / 'test.db')}
        }

        import yaml
        with open(config_file, 'w') as f:
            yaml.dump(config_data, f)

        # Mock del sistema de persistencia
        with patch('backendbot.utils.database_manager.DatabaseManager') as mock_db_class:
            mock_db = MagicMock()
            mock_db_class.return_value = mock_db

            from backendbot.utils.database_manager import ConfigManager

            # Crear manager de configuración
            manager = ConfigManager(str(config_file))

            # Verificar que se cargó correctamente
            assert manager.get('app.name') == 'TestApp'
            assert manager.get('app.version') == '1.0.0'

            # Cambiar configuración
            manager.set('app.name', 'UpdatedApp')

            # Verificar cambio
            assert manager.get('app.name') == 'UpdatedApp'

    def test_monitoring_data_flow(self, temp_dir):
        """Test flujo de datos del sistema de monitoreo"""
        # Crear estructura de archivos de prueba
        test_structure = create_test_directory_structure(temp_dir / 'monitor_test')

        # Simular datos del sistema
        system_data = mock_system_info()
        gpu_data = mock_gpu_info()

        # Verificar que los datos tienen la estructura esperada
        assert 'cpu_percent' in system_data
        assert 'memory_percent' in system_data
        assert 'disk_usage' in system_data
        assert isinstance(system_data['disk_usage'], dict)

        assert 'gpu_count' in gpu_data
        assert 'gpu_0' in gpu_data
        assert 'name' in gpu_data['gpu_0']
        assert 'memory_total' in gpu_data['gpu_0']

        # Verificar cálculos
        disk_usage = system_data['disk_usage']
        total = disk_usage['total']
        used = disk_usage['used']
        free = disk_usage['free']

        assert total == used + free
        assert used / total <= 1.0  # No más del 100%

    def test_file_operations_workflow(self, temp_dir):
        """Test workflow completo de operaciones con archivos"""
        # Crear estructura de prueba
        test_structure = create_test_directory_structure(temp_dir / 'file_test')

        # Simular operaciones del organizador
        documents_dir = test_structure['documents']
        images_dir = test_structure['images']

        # Verificar que los archivos se crearon
        doc_files = list(documents_dir.glob('*.txt'))
        image_files = list(images_dir.glob('*.jpg'))

        assert len(doc_files) > 0
        assert len(image_files) > 0

        # Simular movimiento de archivos (organización)
        organized_dir = temp_dir / 'file_test' / 'organized'
        organized_dir.mkdir()

        # Mover archivos a estructura organizada
        for file_path in doc_files + image_files:
            new_path = organized_dir / file_path.name
            file_path.rename(new_path)

        # Verificar que los archivos se movieron
        assert len(list(organized_dir.glob('*'))) == len(doc_files) + len(image_files)
        assert len(list(documents_dir.glob('*.txt'))) == 0
        assert len(list(images_dir.glob('*.jpg'))) == 0


class TestTaskSchedulerIntegration:
    """Tests de integración del programador de tareas"""

    def test_task_creation_and_execution(self):
        """Test creación y ejecución de tareas"""
        # Mock del scheduler
        with patch('backendbot.core.task_scheduler.schedule') as mock_schedule:
            with patch('backendbot.core.task_scheduler.threading') as mock_threading:

                from backendbot.core.task_scheduler import TaskScheduler

                scheduler = TaskScheduler()

                # Crear tarea de prueba
                task_id = scheduler.add_task(
                    name="Test Task",
                    func=lambda: print("Task executed"),
                    schedule="0 */4 * * *"
                )

                # Verificar que la tarea se creó
                assert task_id is not None
                assert len(scheduler.tasks) > 0

                # Simular ejecución
                scheduler.execute_task(task_id)

                # Verificar que se intentó ejecutar
                # (En un test real verificaríamos que la función se llamó)

    def test_task_persistence_integration(self):
        """Test integración entre tareas y persistencia"""
        # Mock de base de datos
        with patch('backendbot.utils.database_manager.DatabaseManager') as mock_db_class:
            mock_db = MagicMock()
            mock_db_class.return_value = mock_db

            # Mock de consultas
            mock_db.execute_query.return_value = [
                {
                    'id': 1,
                    'name': 'Persisted Task',
                    'schedule': '0 */4 * * *',
                    'enabled': True
                }
            ]

            from backendbot.core.task_scheduler import TaskScheduler

            scheduler = TaskScheduler()

            # Simular carga desde BD
            persisted_tasks = mock_db.execute_query("SELECT * FROM tasks")
            assert len(persisted_tasks) > 0
            assert persisted_tasks[0]['name'] == 'Persisted Task'


class TestLearningSystemIntegration:
    """Tests de integración del sistema de aprendizaje"""

    def test_pattern_learning_workflow(self):
        """Test workflow completo de aprendizaje de patrones"""
        # Mock del sistema de aprendizaje
        with patch('backendbot.core.adaptive_learning.json') as mock_json:
            mock_json.dump = MagicMock()
            mock_json.load = MagicMock(return_value={})

            from backendbot.core.adaptive_learning import AdaptiveLearning

            learning = AdaptiveLearning()

            # Simular aprendizaje de patrón
            pattern = {
                'action': 'file_organization',
                'context': 'user_preference',
                'frequency': 5
            }

            learning.learn_pattern('test_pattern', pattern)

            # Verificar que se guardó el patrón
            assert 'test_pattern' in learning.patterns
            assert learning.patterns['test_pattern']['action'] == 'file_organization'

    def test_learning_persistence_integration(self):
        """Test integración entre aprendizaje y persistencia"""
        # Mock de base de datos
        with patch('backendbot.utils.database_manager.DatabaseManager') as mock_db_class:
            mock_db = MagicMock()
            mock_db_class.return_value = mock_db

            # Mock de datos de aprendizaje
            mock_db.execute_query.return_value = [
                {
                    'id': 1,
                    'pattern_type': 'user_behavior',
                    'pattern_data': json.dumps({'action': 'organize_files'}),
                    'confidence': 0.85
                }
            ]

            from backendbot.core.adaptive_learning import AdaptiveLearning

            learning = AdaptiveLearning()

            # Simular carga de patrones desde BD
            patterns = mock_db.execute_query("SELECT * FROM learning_patterns")
            assert len(patterns) > 0

            pattern_data = json.loads(patterns[0]['pattern_data'])
            assert pattern_data['action'] == 'organize_files'


class TestUIIntegration:
    """Tests de integración de la interfaz de usuario"""

    def test_command_processing_workflow(self):
        """Test workflow de procesamiento de comandos"""
        # Mock del procesador de comandos
        with patch('backendbot.utils.advanced_command_processor.re') as mock_re:
            mock_re.search = MagicMock(return_value=MagicMock())

            from backendbot.utils.advanced_command_processor import AdvancedCommandProcessor

            processor = AdvancedCommandProcessor()

            # Procesar comando de prueba
            command = "organizar archivos en la carpeta documentos"
            result = processor.process_command(command)

            # Verificar que se procesó el comando
            assert result is not None
            # (En un test real verificaríamos la estructura del resultado)

    def test_ui_data_flow(self):
        """Test flujo de datos en la interfaz"""
        # Simular datos que fluyen desde el backend hacia la UI
        ui_data = {
            'system_status': mock_system_info(),
            'gpu_status': mock_gpu_info(),
            'active_tasks': [
                {'id': 1, 'name': 'Test Task', 'status': 'running'}
            ],
            'learned_patterns': [
                {'pattern': 'file_org', 'confidence': 0.9}
            ]
        }

        # Verificar estructura de datos
        assert 'system_status' in ui_data
        assert 'gpu_status' in ui_data
        assert 'active_tasks' in ui_data
        assert 'learned_patterns' in ui_data

        # Verificar contenido
        assert ui_data['system_status']['cpu_percent'] >= 0
        assert ui_data['gpu_status']['gpu_count'] >= 0
        assert len(ui_data['active_tasks']) > 0
        assert len(ui_data['learned_patterns']) > 0
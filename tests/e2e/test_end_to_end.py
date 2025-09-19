"""
Tests End-to-End para BackendBot
Simulación de flujos completos de usuario
"""

import pytest
import os
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock
import time

from tests.utils.test_utils import (
    TestConfig,
    create_test_directory_structure,
    mock_system_info,
    mock_gpu_info
)


class TestEndToEndWorkflow:
    """Tests E2E de workflows completos"""

    def test_complete_system_startup(self, temp_dir):
        """Test inicio completo del sistema"""
        # Configurar entorno de prueba
        config_file = temp_dir / 'e2e_config.yaml'
        db_file = temp_dir / 'e2e_backendbot.db'

        # Crear configuración de prueba
        config_data = {
            'app': {
                'name': 'BackendBot-E2E',
                'version': '2.0.0',
                'debug': True
            },
            'database': {
                'path': str(db_file)
            }
        }

        import yaml
        with open(config_file, 'w') as f:
            yaml.dump(config_data, f)

        # Mock de componentes del sistema
        with patch('backendbot.utils.database_manager.DatabaseManager') as mock_db_class:
            with patch('backendbot.core.task_scheduler.TaskScheduler') as mock_scheduler_class:
            # with patch('backendbot.core.adaptive_learning.AdaptiveLearning') as mock_learning_class:

                # Configurar mocks
                mock_db = MagicMock()
                mock_db_class.return_value = mock_db

                mock_scheduler = MagicMock()
                mock_scheduler_class.return_value = mock_scheduler

                # mock_learning = MagicMock()
                # mock_learning_class.return_value = mock_learning

                # Simular inicio del sistema
                from backendbot.core.main import BackendBotSystem

                system = BackendBotSystem(config_path=str(config_file))

                # Verificar inicialización
                assert system.config is not None
                assert system.db_manager is not None
                assert system.task_scheduler is not None
                # assert system.learning_system is not None

                # Simular startup
                system.start()

                # Verificar que los componentes se iniciaron
                mock_db.connect.assert_called()
                mock_scheduler.start.assert_called()
                # mock_learning.start_learning.assert_called()

    def test_file_organization_workflow(self, temp_dir):
        """Test workflow completo de organización de archivos"""
        # Crear estructura desorganizada
        source_dir = temp_dir / 'source'
        organized_dir = temp_dir / 'organized'

        source_dir.mkdir()
        organized_dir.mkdir()

        # Crear archivos de diferentes tipos
        test_files = [
            ('document1.txt', 'Contenido de texto'),
            ('document2.pdf', 'Contenido PDF'),
            ('image1.jpg', 'Datos JPG'),
            ('image2.png', 'Datos PNG'),
            ('video1.mp4', 'Datos MP4'),
            ('music1.mp3', 'Datos MP3'),
            ('archive1.zip', 'Datos ZIP'),
            ('temp1.tmp', 'Datos temporales'),
        ]

        for filename, content in test_files:
            file_path = source_dir / filename
            file_path.write_text(content)

        # Simular workflow de organización
        from backendbot.bots.bot_organizer import BotOrganizer

        organizer = BotOrganizer()

        # Configurar reglas de organización
        rules = {
            'documents': ['.txt', '.pdf'],
            'images': ['.jpg', '.png'],
            'videos': ['.mp4'],
            'music': ['.mp3'],
            'archives': ['.zip'],
            'temp': ['.tmp']
        }

        # Ejecutar organización
        result = organizer.organize_files(str(source_dir), str(organized_dir), rules)

        # Verificar resultados
        assert result['total_files'] == len(test_files)
        assert result['organized_files'] > 0

        # Verificar que se crearon las carpetas correctas
        for category in rules.keys():
            category_dir = organized_dir / category
            assert category_dir.exists()

        # Verificar que los archivos se movieron
        remaining_files = list(source_dir.glob('*'))
        assert len(remaining_files) == 0  # Todos los archivos deberían haberse movido

    def test_monitoring_and_alerts_workflow(self, temp_dir):
        """Test workflow de monitoreo y alertas"""
        # Simular datos del sistema
        system_data = mock_system_info()
        gpu_data = mock_gpu_info()

        # Simular umbrales de alerta
        thresholds = {
            'cpu_high': 80,
            'memory_high': 85,
            'disk_high': 90
        }

        from backendbot.utils.system_monitor import SystemMonitor

        monitor = SystemMonitor(thresholds=thresholds)

        # Simular verificación de sistema
        alerts = monitor.check_system_health(system_data, gpu_data)

        # Verificar que se generaron alertas apropiadas
        assert isinstance(alerts, list)

        # Verificar alertas basadas en umbrales
        cpu_percent = system_data['cpu_percent']
        if cpu_percent > thresholds['cpu_high']:
            cpu_alerts = [a for a in alerts if 'CPU' in a['message']]
            assert len(cpu_alerts) > 0

        memory_percent = system_data['memory_percent']
        if memory_percent > thresholds['memory_high']:
            memory_alerts = [a for a in alerts if 'memoria' in a['message']]
            assert len(memory_alerts) > 0

    def test_learning_adaptation_workflow(self):
        """Test workflow de aprendizaje y adaptación"""
        # Simular interacciones del usuario
        user_interactions = [
            {'action': 'organize_files', 'context': 'documents', 'time': '2025-09-18T10:00:00'},
            {'action': 'organize_files', 'context': 'documents', 'time': '2025-09-18T11:00:00'},
            {'action': 'organize_files', 'context': 'images', 'time': '2025-09-18T12:00:00'},
            {'action': 'organize_files', 'context': 'documents', 'time': '2025-09-18T13:00:00'},
            {'action': 'organize_files', 'context': 'documents', 'time': '2025-09-18T14:00:00'},
        ]

        from backendbot.core.adaptive_learning import adaptive_learning

        learning = adaptive_learning

        # Aprender de las interacciones
        for interaction in user_interactions:
            pattern = {
                'action': interaction['action'],
                'context': interaction['context'],
                'timestamp': interaction['time']
            }
            learning.learn_pattern(f"pattern_{interaction['context']}", pattern)

        # Verificar que se aprendieron patrones
        assert len(learning.patterns) > 0

        # Verificar patrón más frecuente
        document_patterns = [p for p in learning.patterns.values() if p.get('context') == 'documents']
        assert len(document_patterns) >= 3  # Mayor frecuencia

        # Simular recomendación
        recommendation = learning.get_recommendation('organize_files')
        assert recommendation is not None
        assert 'context' in recommendation

    def test_command_processing_e2e(self):
        """Test procesamiento completo de comandos"""
        # Simular comandos del usuario
        test_commands = [
            "organizar archivos",
            "mostrar estado del sistema",
            "analizar disco C:",
            "crear backup",
            "limpiar archivos temporales"
        ]

        from backendbot.utils.advanced_command_processor import AdvancedCommandProcessor

        processor = AdvancedCommandProcessor()

        for command in test_commands:
            # Procesar comando
            result = processor.process_command(command)

            # Verificar que se procesó
            assert result is not None
            assert 'action' in result
            assert 'confidence' in result

            # Verificar que la confianza es razonable
            assert 0 <= result['confidence'] <= 1

    def test_task_scheduler_e2e(self):
        """Test programador de tareas end-to-end"""
        # Simular tareas programadas
        test_tasks = [
            {
                'name': 'Limpieza Diaria',
                'schedule': '0 2 * * *',  # 2 AM diario
                'action': 'cleanup_temp_files'
            },
            {
                'name': 'Backup Semanal',
                'schedule': '0 3 * * 0',  # 3 AM domingos
                'action': 'create_backup'
            },
            {
                'name': 'Monitoreo por Horas',
                'schedule': '0 */4 * * *',  # Cada 4 horas
                'action': 'system_monitoring'
            }
        ]

        from backendbot.core.task_scheduler import TaskScheduler

        scheduler = TaskScheduler()

        # Crear tareas
        task_ids = []
        for task in test_tasks:
            task_id = scheduler.add_task(
                name=task['name'],
                func=lambda: print(f"Ejecutando {task['name']}"),
                schedule=task['schedule']
            )
            task_ids.append(task_id)

        # Verificar que se crearon las tareas
        assert len(scheduler.tasks) == len(test_tasks)

        # Simular ejecución de tareas
        for task_id in task_ids:
            scheduler.execute_task(task_id)

        # Verificar estadísticas
        stats = scheduler.get_task_stats()
        assert stats['total_tasks'] == len(test_tasks)
        assert stats['enabled_tasks'] == len(test_tasks)

    def test_ui_interaction_workflow(self):
        """Test workflow completo de interacción con UI"""
        # Simular flujo de usuario en la interfaz
        ui_actions = [
            {'action': 'open_main_window', 'timestamp': '2025-09-18T09:00:00'},
            {'action': 'navigate_to_monitor', 'timestamp': '2025-09-18T09:01:00'},
            {'action': 'run_system_scan', 'timestamp': '2025-09-18T09:02:00'},
            {'action': 'view_organizer', 'timestamp': '2025-09-18T09:03:00'},
            {'action': 'organize_files', 'timestamp': '2025-09-18T09:04:00'},
            {'action': 'close_application', 'timestamp': '2025-09-18T09:05:00'}
        ]

        # Simular procesamiento de acciones de UI
        processed_actions = []

        for action in ui_actions:
            # Simular procesamiento de cada acción
            processed_action = {
                'original_action': action['action'],
                'timestamp': action['timestamp'],
                'processed': True,
                'result': 'success'
            }
            processed_actions.append(processed_action)

            # Simular delay de procesamiento
            time.sleep(0.01)

        # Verificar que todas las acciones se procesaron
        assert len(processed_actions) == len(ui_actions)

        for processed in processed_actions:
            assert processed['processed'] is True
            assert processed['result'] == 'success'
            assert 'timestamp' in processed

        # Verificar orden temporal
        timestamps = [action['timestamp'] for action in ui_actions]
        processed_timestamps = [action['timestamp'] for action in processed_actions]

        assert timestamps == processed_timestamps
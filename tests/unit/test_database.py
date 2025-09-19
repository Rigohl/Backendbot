"""
Tests Unitarios para el Sistema de Persistencia
BackendBot v2.0.0
"""

import pytest
import os
import tempfile
import json
from pathlib import Path
from unittest.mock import patch, MagicMock
from datetime import datetime

from tests.utils.test_utils import TestDataFactory, MockDatabaseManager


class TestDatabaseManager:
    """Tests para DatabaseManager"""

    def test_connect_success(self, mock_db):
        """Test conexión exitosa a base de datos"""
        connection = mock_db.connect()
        assert mock_db.connected is True
        assert connection is not None

    def test_execute_query(self, mock_db):
        """Test ejecución de consultas SELECT"""
        mock_db.connect()

        # Test consulta de usuarios
        users = mock_db.execute_query("SELECT * FROM users")
        assert isinstance(users, list)
        assert len(users) > 0
        assert 'username' in users[0]

        # Test consulta de tareas
        tasks = mock_db.execute_query("SELECT * FROM tasks")
        assert isinstance(tasks, list)
        assert len(tasks) > 0
        assert 'name' in tasks[0]

    def test_execute_update(self, mock_db):
        """Test ejecución de consultas INSERT/UPDATE/DELETE"""
        mock_db.connect()

        result = mock_db.execute_update("INSERT INTO users (username) VALUES (?)", ("test",))
        assert result == 1

    def test_disconnect(self, mock_db):
        """Test desconexión de base de datos"""
        mock_db.connect()
        mock_db.disconnect()
        assert mock_db.connected is False


class TestConfigManager:
    """Tests para ConfigManager"""

    @pytest.fixture
    def temp_config_file(self, temp_dir):
        """Fixture que crea un archivo de configuración temporal"""
        config_file = temp_dir / 'test_config.yaml'
        config_data = {
            'app': {
                'name': 'TestApp',
                'version': '1.0.0'
            },
            'test': {
                'value': 42
            }
        }

        import yaml
        with open(config_file, 'w') as f:
            yaml.dump(config_data, f)

        return config_file

    def test_get_existing_value(self, temp_config_file):
        """Test obtener valor existente"""
        with patch('backendbot.utils.database_manager.ConfigManager._ensure_config_directory'):
            with patch('backendbot.utils.database_manager.ConfigManager._load_config'):
                from backendbot.utils.database_manager import ConfigManager

                manager = ConfigManager(str(temp_config_file))
                manager.config = {'app': {'name': 'TestApp'}}

                value = manager.get('app.name')
                assert value == 'TestApp'

    def test_get_nonexistent_value(self, temp_config_file):
        """Test obtener valor inexistente con default"""
        with patch('backendbot.utils.database_manager.ConfigManager._ensure_config_directory'):
            with patch('backendbot.utils.database_manager.ConfigManager._load_config'):
                from backendbot.utils.database_manager import ConfigManager

                manager = ConfigManager(str(temp_config_file))
                manager.config = {}

                value = manager.get('nonexistent.key', 'default')
                assert value == 'default'

    def test_set_value(self, temp_config_file):
        """Test establecer valor de configuración"""
        with patch('backendbot.utils.database_manager.ConfigManager._ensure_config_directory'):
            with patch('backendbot.utils.database_manager.ConfigManager._save_config'):
                from backendbot.utils.database_manager import ConfigManager

                manager = ConfigManager(str(temp_config_file))
                manager.config = {}

                manager.set('test.value', 123)
                assert manager.config['test']['value'] == 123


class TestMigrationManager:
    """Tests para MigrationManager"""

    @pytest.fixture
    def temp_migration_dir(self, temp_dir):
        """Fixture que crea un directorio de migraciones temporal"""
        migration_dir = temp_dir / 'migrations'
        migration_dir.mkdir()

        # Crear migración de prueba
        migration_file = migration_dir / '001_test_migration.sql'
        migration_file.write_text('CREATE TABLE test_table (id INTEGER PRIMARY KEY);')

        return migration_dir

    def test_run_migrations(self, temp_migration_dir):
        """Test ejecución de migraciones"""
        with patch('backendbot.utils.database_manager.DatabaseManager') as mock_db_class:
            mock_db = MagicMock()
            mock_db_class.return_value = mock_db

            from backendbot.utils.database_manager import MigrationManager

            manager = MigrationManager(mock_db)
            manager.migrations_dir = str(temp_migration_dir)

            # Mock para evitar ejecución real
            mock_db.execute_query.return_value = []
            mock_db.execute_update.return_value = None

            manager.run_migrations()

            # Verificar que se intentó ejecutar la migración
            assert mock_db.execute_update.called


class TestDataFactoryTests:
    """Tests para la fábrica de datos de prueba (evita conflicto con fixture TestDataFactory)"""

    def test_create_user(self):
        """Test creación de usuario de prueba"""
        from tests.utils.test_utils import TestDataFactory as Factory

        user = Factory.create_user("testuser", preferences={'theme': 'dark'})

        assert user['username'] == 'testuser'
        assert user['id'] == 1
        assert 'created_at' in user
        assert 'updated_at' in user

        preferences = json.loads(user['preferences'])
        assert preferences['theme'] == 'dark'

    def test_create_task(self):
        """Test creación de tarea de prueba"""
        from tests.utils.test_utils import TestDataFactory as Factory

        task = Factory.create_task("Test Task", description="Descripción")

        assert task['name'] == 'Test Task'
        assert task['description'] == 'Descripción'
        assert task['enabled'] is True
        assert 'schedule' in task

    def test_create_metric(self):
        """Test creación de métrica de prueba"""
        from tests.utils.test_utils import TestDataFactory as Factory

        metric = Factory.create_metric("cpu", 75.5, unit="%", metadata={'core': 0})

        assert metric['metric_type'] == 'cpu'
        assert metric['value'] == 75.5
        assert metric['unit'] == '%'

        metadata = json.loads(metric['metadata'])
        assert metadata['core'] == 0


class TestMockDatabaseManager:
    """Tests para MockDatabaseManager"""

    def test_mock_connection(self):
        """Test conexión mock"""
        mock_db = MockDatabaseManager()
        connection = mock_db.connect()

        assert mock_db.connected is True
        assert connection is not None

    def test_mock_query_execution(self):
        """Test ejecución de consultas mock"""
        mock_db = MockDatabaseManager()
        mock_db.connect()

        users = mock_db.execute_query("SELECT * FROM users")
        assert len(users) == 1
        assert users[0]['username'] == 'test_user'

        tasks = mock_db.execute_query("SELECT * FROM tasks")
        assert len(tasks) == 1
        assert tasks[0]['name'] == 'Test Task'

    def test_mock_update_execution(self):
        """Test ejecución de updates mock"""
        mock_db = MockDatabaseManager()
        mock_db.connect()

        result = mock_db.execute_update("INSERT INTO test VALUES (?)", ("value",))
        assert result == 1